"""Safe OCR Service wrapper using PyTesseract with graceful fallbacks (Phase 8)."""

import time
from typing import List, Optional
import pytesseract
from PIL import Image

from app.core.logging import logger
from app.ingestion.limits import limits
from app.ocr.base import BaseOCRService, OCRBoundingBox, OCREvidenceWord, OCRResult
from app.ocr.preprocessing import image_preprocessor


class SafeOCRService(BaseOCRService):
    """Executes OCR extraction with resource timeouts, confidence scoring, and fallback handling."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_bytes: bytes) -> OCRResult:
        start_t = time.perf_counter()
        warnings: List[str] = []

        try:
            img = image_preprocessor.validate_and_load(image_bytes)
            processed_img = image_preprocessor.enhance_for_ocr(img)
        except Exception as e:
            return OCRResult(
                extracted_text="",
                confidence=0.0,
                word_count=0,
                words=[],
                processing_time_ms=round((time.perf_counter() - start_t) * 1000, 2),
                warnings=[f"Image preprocessing failed: {str(e)}"],
                engine_name="SafeOCR-Preprocessor",
            )

        extracted_text = ""
        avg_confidence = 0.0
        words: List[OCREvidenceWord] = []

        try:
            # Extract detailed data with bounding boxes and confidence
            data = pytesseract.image_to_data(
                processed_img,
                output_type=pytesseract.Output.DICT,
                timeout=limits.OCR_PROCESSING_TIMEOUT_SECONDS,
            )

            confidences = []
            extracted_tokens = []

            for i in range(len(data["text"])):
                token = data["text"][i].strip()
                conf_str = data["conf"][i]
                
                try:
                    conf = float(conf_str)
                except (ValueError, TypeError):
                    conf = -1.0

                if token and conf >= 0:
                    conf_scaled = max(0.0, min(1.0, conf / 100.0))
                    confidences.append(conf_scaled)
                    extracted_tokens.append(token)
                    
                    words.append(
                        OCREvidenceWord(
                            text=token,
                            confidence=round(conf_scaled, 4),
                            bounding_box=OCRBoundingBox(
                                x=float(data["left"][i]),
                                y=float(data["top"][i]),
                                width=float(data["width"][i]),
                                height=float(data["height"][i]),
                            ),
                        )
                    )

            extracted_text = " ".join(extracted_tokens).strip()
            avg_confidence = (sum(confidences) / len(confidences)) if confidences else 0.0

            if avg_confidence < limits.LOW_OCR_CONFIDENCE_THRESHOLD and extracted_text:
                warnings.append("Low OCR confidence — verify original image quality and resolution.")

        except pytesseract.TesseractNotFoundError:
            logger.warning("Tesseract binary not found on system PATH. OCR falling back to image metadata analysis.")
            warnings.append("OCR engine binary not configured on host environment.")
            extracted_text = ""
            avg_confidence = 0.0
        except pytesseract.TesseractError as te:
            logger.warning(f"Tesseract extraction error: {te}")
            warnings.append(f"OCR processing error: {str(te)}")
        except Exception as e:
            logger.exception(f"Unexpected OCR failure: {e}")
            warnings.append(f"OCR failure: {str(e)}")

        duration_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return OCRResult(
            extracted_text=extracted_text,
            confidence=round(avg_confidence, 4),
            word_count=len(words),
            words=words,
            processing_time_ms=duration_ms,
            warnings=warnings,
            engine_name="Tesseract-OCR",
        )


ocr_service = SafeOCRService()
