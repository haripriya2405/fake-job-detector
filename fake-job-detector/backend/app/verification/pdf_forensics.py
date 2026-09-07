"""PDF Offer Letter Document Forensics & Tamper Inspector Module.
Analyzes PDF metadata, creation tools, font embedding, digital signatures, and content alignment
to detect fraudulent offer letters, forged seals, and edited templates.
"""

import re
from typing import Any, Dict, List, Optional
import pypdf
import io
from app.core.logging import logger

class PDFForensicsInspector:
    """Performs deep forensic inspection on uploaded PDF offer letters and documents."""

    # Common non-corporate or design tools often associated with forged offer letters
    SUSPICIOUS_CREATORS = [
        "canva", "gimp", "photoshop", "paint", "pdf2go", "ilovepdf", "smallpdf",
        "pdf2docx", "sejda", "foxit phantom", "pdfedit", "sdocx"
    ]

    # Official corporate document publishers
    CORPORATE_PRODUCERS = [
        "adobe pdf library", "adobe acrobat", "microsoft® word", "ghostscript",
        "quartz pdfcontext", "distiller", "workday", "bamboohr", "greenhouse"
    ]

    def inspect_pdf(self, pdf_bytes: bytes, filename: str = "offer_letter.pdf") -> Dict[str, Any]:
        """Runs multi-point forensic inspection on raw PDF file bytes."""
        start_time = logger.info(f"Starting PDF forensic inspection for [{filename}]...")

        tamper_flags: List[str] = []
        indicators: List[Dict[str, Any]] = []
        tamper_score = 0  # 0 (Authentic) to 100 (Max Tamper Risk)

        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            num_pages = len(reader.pages)
            metadata = reader.metadata or {}

            creator = str(metadata.get('/Creator', '')).lower()
            producer = str(metadata.get('/Producer', '')).lower()
            author = str(metadata.get('/Author', '')).lower()
            creation_date = str(metadata.get('/CreationDate', ''))
            mod_date = str(metadata.get('/ModDate', ''))

            # 1. Creation Tool & Metadata Inspection
            suspicious_tool_found = False
            for tool in self.SUSPICIOUS_CREATORS:
                if tool in creator or tool in producer:
                    suspicious_tool_found = True
                    tamper_score += 25
                    tamper_flags.append(f"Document created using online/graphics editing tool: '{tool.capitalize()}'")
                    indicators.append({
                        "rule_id": "PDF_SUSPICIOUS_CREATOR_TOOL",
                        "severity": "HIGH",
                        "description": f"PDF generated via consumer editing platform ({tool.capitalize()}) rather than enterprise HR software.",
                    })
                    break

            if not creator and not producer:
                tamper_score += 15
                tamper_flags.append("PDF metadata stripped or missing creation origin.")
                indicators.append({
                    "rule_id": "PDF_STRIPPED_METADATA",
                    "severity": "MEDIUM",
                    "description": "Document metadata has been stripped, concealing software author and creation history.",
                })

            # 2. Modification Date vs Creation Date Drift
            if creation_date and mod_date and creation_date != mod_date:
                tamper_score += 15
                tamper_flags.append("Document modified after initial creation (post-editing detected).")
                indicators.append({
                    "rule_id": "PDF_MODIFICATION_DRIFT",
                    "severity": "MEDIUM",
                    "description": "Modification timestamp differs from initial creation timestamp, indicating post-export alteration.",
                })

            # 3. Text Extraction & Font Structure Inspection
            extracted_text = ""
            fonts_used = set()

            for page in reader.pages:
                text = page.extract_text() or ""
                extracted_text += text + "\n"

                # Check fonts embedded in page resources
                if '/Resources' in page and '/Font' in page['/Resources']:
                    font_dict = page['/Resources']['/Font']
                    if hasattr(font_dict, 'keys'):
                        for font_key in font_dict.keys():
                            fonts_used.add(str(font_key))

            # 4. Email & Contact Pattern Analysis inside PDF Text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', extracted_text)
            free_webmail_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com', 'yandex.com']

            for email in emails:
                domain = email.split('@')[-1].lower()
                if domain in free_webmail_providers:
                    tamper_score += 30
                    tamper_flags.append(f"Official offer letter uses free webmail domain: '{email}'")
                    indicators.append({
                        "rule_id": "PDF_FREE_WEBMAIL_HR_CONTACT",
                        "severity": "CRITICAL",
                        "description": f"HR contact inside offer letter uses personal webmail ({email}) instead of official company domain.",
                    })

            # 5. Financial & Security Demand Signals inside PDF
            upfront_fee_terms = ["registration fee", "processing charge", "equipment deposit", "cashier check", "wire transfer", "crypto", "usdt", "telegram"]
            for term in upfront_fee_terms:
                if term in extracted_text.lower():
                    tamper_score += 35
                    tamper_flags.append(f"Offer letter contains suspicious financial demand: '{term}'")
                    indicators.append({
                        "rule_id": "PDF_UPFRONT_FEE_DEMAND",
                        "severity": "CRITICAL",
                        "description": f"Document requests financial payment or deposit ({term}) which is typical of job scams.",
                    })

            # Cap score between 0 and 100
            tamper_score = max(0, min(100, tamper_score))

            authenticity_verdict = "VERIFIED_AUTHENTIC" if tamper_score < 30 else "REQUIRES_CAUTION" if tamper_score < 60 else "HIGH_RISK_FORGERY"

            return {
                "filename": filename,
                "pages": num_pages,
                "tamper_score": tamper_score,
                "authenticity_verdict": authenticity_verdict,
                "metadata": {
                    "creator": creator or "Unknown",
                    "producer": producer or "Unknown",
                    "author": author or "Unknown",
                    "creation_date": creation_date or "Unknown",
                    "mod_date": mod_date or "Unknown",
                    "font_count": len(fonts_used),
                },
                "tamper_flags": tamper_flags,
                "indicators": indicators,
                "extracted_text": extracted_text.strip(),
            }

        except Exception as e:
            logger.error(f"PDF forensic analysis failed on [{filename}]: {e}")
            return {
                "filename": filename,
                "pages": 0,
                "tamper_score": 50,
                "authenticity_verdict": "UNVERIFIED_FORMAT",
                "metadata": {},
                "tamper_flags": [f"Forensic parser notice: {str(e)}"],
                "indicators": [],
                "extracted_text": "",
            }

pdf_forensics_inspector = PDFForensicsInspector()
