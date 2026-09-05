import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np

from app.core.logging import logger
from app.ml.preprocessing import preprocessor
from app.ml.schemas import MLFeatureContribution, MLPredictionOutput


class MLPredictor:
    """Production inference service for evaluating job posting fraud likelihood with DeBERTa ONNX or Classic ML."""

    def __init__(
        self,
        artifact_path: Optional[str] = None,
        artifacts_dir: str = "artifacts/models",
    ):
        self.artifacts_dir = artifacts_dir
        self.artifact_path = artifact_path
        self.model = None
        self.onnx_session = None
        self.tokenizer = None
        self.metadata = {}
        self.model_version = "pending"
        self.algorithm = "pending"
        self.model_type = "none"  # "onnx" | "sklearn" | "none"

        self._load_active_model()

    def reload_model(self, artifact_path: Optional[str] = None) -> bool:
        """Reload or switch the active ML model artifact."""
        self.artifact_path = artifact_path
        return self._load_active_model()

    def _load_active_model(self) -> bool:
        """Locate and load the verified model artifact and metadata."""
        if not self.artifact_path:
            if os.path.exists(self.artifacts_dir):
                # Production Governance: Active production is logisticregression-v1.0.0 unless explicit path is provided
                logreg_default = os.path.join(self.artifacts_dir, "tfidf_logistic_regression_v1.0.0.joblib")
                if os.path.exists(logreg_default):
                    self.artifact_path = logreg_default
                else:
                    joblib_candidates = [f for f in os.listdir(self.artifacts_dir) if f.endswith(".joblib")]
                    onnx_candidates = [f for f in os.listdir(self.artifacts_dir) if f.endswith(".onnx")]
                    if joblib_candidates:
                        joblib_candidates.sort(reverse=True)
                        self.artifact_path = os.path.join(self.artifacts_dir, joblib_candidates[0])
                    elif onnx_candidates:
                        onnx_candidates.sort(reverse=True)
                        self.artifact_path = os.path.join(self.artifacts_dir, onnx_candidates[0])

        if not self.artifact_path or not os.path.exists(self.artifact_path):
            logger.warning(f"No valid model artifact found at '{self.artifact_path}'. Inference will remain in pending state.")
            return False

        try:
            is_onnx = self.artifact_path.endswith(".onnx")
            meta_path = self.artifact_path.replace(".onnx" if is_onnx else ".joblib", ".meta.json")

            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

                # Check SHA256 integrity
                expected_sha = self.metadata.get("sha256_checksum")
                if expected_sha:
                    with open(self.artifact_path, "rb") as f:
                        actual_sha = hashlib.sha256(f.read()).hexdigest()
                    if actual_sha != expected_sha:
                        logger.error(f"Model integrity checksum mismatch for {self.artifact_path}!")
                        return False

                self.model_version = self.metadata.get("model_version", self.metadata.get("version", "1.0.0"))
                self.algorithm = self.metadata.get("algorithm", "DeBERTa-v3-ONNX" if is_onnx else "LogisticRegression")
            else:
                self.model_version = "v1.0.0"
                self.algorithm = "DeBERTa-v3-ONNX" if is_onnx else "LogisticRegression"

            if is_onnx:
                import onnxruntime as ort
                from transformers import AutoTokenizer

                logger.info(f"Loading ONNX Runtime Transformer session from {self.artifact_path}...")
                sess_options = ort.SessionOptions()
                sess_options.intra_op_num_threads = 2
                self.onnx_session = ort.InferenceSession(self.artifact_path, sess_options)

                # Load tokenizer
                tokenizer_dir = self.metadata.get("tokenizer_dir")
                base_model = self.metadata.get("base_model", "microsoft/deberta-v3-small")
                if tokenizer_dir and os.path.exists(tokenizer_dir):
                    self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
                else:
                    self.tokenizer = AutoTokenizer.from_pretrained(base_model)

                self.model_type = "onnx"
                self.model = self.onnx_session
            else:
                self.model = joblib.load(self.artifact_path)
                self.model_type = "sklearn"

            logger.info(f"Loaded ML model: {self.algorithm} (Version: {self.model_version}, Type: {self.model_type}) from {self.artifact_path}")
            return True
        except Exception as e:
            logger.exception(f"Failed to load ML artifact from {self.artifact_path}: {e}")
            self.model = None
            self.onnx_session = None
            self.model_type = "none"
            return False

    def is_model_loaded(self) -> bool:
        return self.model is not None or self.onnx_session is not None

    def predict(self, raw_text: str) -> Optional[MLPredictionOutput]:
        """Perform classification inference using either ONNX Transformer or scikit-learn pipeline."""
        if not self.is_model_loaded() or not raw_text:
            return None

        if self.model_type == "onnx":
            return self._predict_onnx_transformer(raw_text)
        else:
            return self._predict_sklearn(raw_text)

    def _predict_onnx_transformer(self, raw_text: str) -> MLPredictionOutput:
        """Inference path for ONNX Transformer with token highlight extraction."""
        max_length = self.metadata.get("max_length", 512)
        encoded = self.tokenizer(
            raw_text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="np",
        )

        onnx_inputs = {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64),
        }

        outputs = self.onnx_session.run(None, onnx_inputs)
        logits = outputs[0][0]

        # Softmax probability calculation
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()
        prob_fraud = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])

        label = "suspicious" if prob_fraud >= 0.50 else "legitimate"
        confidence_scaled = round(prob_fraud * 100.0, 2)

        # Extract highlighted manipulation spans and top features
        top_features, highlight_spans = self._extract_transformer_manipulation_spans(raw_text, prob_fraud)

        return MLPredictionOutput(
            label=label,
            probability=round(prob_fraud, 4),
            confidence_score=confidence_scaled,
            model_version=f"{self.algorithm.lower()}-{self.model_version}",
            algorithm=self.algorithm,
            top_features=top_features,
            highlight_spans=highlight_spans,
            decision_threshold=0.50,
        )

    def _extract_transformer_manipulation_spans(
        self, text: str, fraud_prob: float
    ) -> Tuple[List[MLFeatureContribution], List[Dict[str, Any]]]:
        """Isolate manipulative sentence clauses and suspicious token spans using contextual heuristics & NLP."""
        import unicodedata

        # Transliterate Cyrillic / visual lookalike homoglyphs to Latin equivalents
        cyrillic_map = {
            'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
            'і': 'i', 'ј': 'j', 'ѕ': 's', 'ԁ': 'd', 'ԛ': 'q', 'ԝ': 'w',
            'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O',
            'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X', 'І': 'I', 'Ј': 'J', 'Ѕ': 'S'
        }
        normalized_text = unicodedata.normalize("NFKC", text)
        dehomoglyphed = "".join(cyrillic_map.get(c, c) for c in normalized_text)

        manipulation_triggers = [
            # Fake checks with punctuation/spacing tolerance
            (r"(?:advance|c[\s\.\-_]*a[\s\.\-_]*s[\s\.\-_]*h[\s\.\-_]*i[\s\.\-_]*e[\s\.\-_]*r|clearing)\s*[\.\-_]*\s*(?:c[\s\.\-_]*h[\s\.\-_]*e[\s\.\-_]*c[\s\.\-_]*k|cheque|deposit)", "fake_check_reimbursement", 0.95),
            # Upfront fees, security deposits, courier insurance, test bench fees
            (r"(?:r[\s\.\-_]*e[\s\.\-_]*g[\s\.\-_]*i[\s\.\-_]*s[\s\.\-_]*t[\s\.\-_]*r[\s\.\-_]*a[\s\.\-_]*t[\s\.\-_]*i[\s\.\-_]*o[\s\.\-_]*n|processing|interview|courier\s+insurance|security|onboarding|test\s+bench|screening|verification|application)\s*(?:fee|contribution|deposit|bond)", "upfront_fee_demand", 0.98),
            # Direct payment commands disguised as fees
            (r"(?:pay|deposit|transfer)\s+(?:r[\s\.\-_]*e[\s\.\-_]*g[\s\.\-_]*i[\s\.\-_]*s[\s\.\-_]*t[\s\.\-_]*r[\s\.\-_]*a[\s\.\-_]*t[\s\.\-_]*i[\s\.\-_]*o[\s\.\-_]*n|\$\d+|rs\.?\s*\d+)", "upfront_fee_demand", 0.97),
            # Channel diversion (Telegram / WhatsApp with spaced characters)
            (r"(?:t[\s\.\-_]*e[\s\.\-_]*l[\s\.\-_]*e[\s\.\-_]*g[\s\.\-_]*r[\s\.\-_]*a[\s\.\-_]*m|whatsapp|signal|t\.me)\b", "channel_diversion", 0.90),
            # Artificial urgency
            (r"(?:within\s+\d+\s+hours?|urgent\s+selection|immediate\s+offer)", "artificial_urgency", 0.82),
            # Fast-track / interview waiver
            (r"(?:waived|skip)\s+(?:interview|technical\s+round)", "phantom_fast_track", 0.88),
            # Crypto task, brush ratings, and workstation balance
            (r"(?:fund|recharge|optimize|rating)\s+.*?(?:wallet|w\s*a\s*l\s*l\s*e\s*t|workstation\s+balance|balance\s+with\s+\$\d+|vip|u\s*s\s*d\s*t)", "crypto_task_trap", 0.96),
            (r"(?:transfer|pay)\s+\d+\s*(?:usdt|u\s*s\s*d\s*t|crypto|btc)", "crypto_task_trap", 0.97),
            (r"(?:product\s+optimization\s+tasks|commission\s+settlements)", "crypto_task_trap", 0.92),
            # Typosquatted / untrusted TLD links
            (r"https?://[^\s]+\.(?:xyz|top|work|click|club|biz|tk|gq|ml)\b", "phishing_domain_lure", 0.96),
            # Credential and OTP theft
            (r"(?:netbanking|password|otp|pin|authentication\s+pin)\s+(?:verification|submission|sent|to\s+your\s+phone)", "credential_harvesting", 0.99),
            (r"(?:online\s+banking\s+username|password|pin)", "credential_harvesting", 0.99),
        ]

        features: List[MLFeatureContribution] = []
        highlight_spans: List[Dict[str, Any]] = []

        # Match against de-homoglyphed text and map back to original indices
        for pattern, pattern_type, weight in manipulation_triggers:
            for match in re.finditer(pattern, dehomoglyphed, re.IGNORECASE):
                start, end = match.span()
                matched_token = text[start:end] if end <= len(text) else match.group(0)
                
                # Expand to enclosing sentence for context
                sent_start = max(0, text.rfind(".", 0, start) + 1)
                sent_end = text.find(".", end)
                if sent_end == -1:
                    sent_end = len(text)
                sentence = text[sent_start:sent_end].strip()

                features.append(
                    MLFeatureContribution(
                        token=matched_token,
                        weight=round(weight * fraud_prob, 4),
                        direction="suspicious",
                        start_char=start,
                        end_char=end,
                        context_sentence=sentence,
                    )
                )

                highlight_spans.append({
                    "start": start,
                    "end": end,
                    "matched_text": matched_token,
                    "category": pattern_type,
                    "context_sentence": sentence,
                    "risk_weight": round(weight, 2),
                })

        features.sort(key=lambda x: x.weight, reverse=True)
        return features[:6], highlight_spans

    def _predict_sklearn(self, raw_text: str) -> MLPredictionOutput:
        """Inference path for legacy scikit-learn models."""
        cleaned = preprocessor.clean_text(raw_text)
        if not cleaned:
            return MLPredictionOutput(
                label="legitimate",
                probability=0.0,
                confidence_score=0.0,
                model_version=self.model_version,
                algorithm=self.algorithm,
                top_features=[],
            )

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba([cleaned])[0]
            prob_fraud = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            pred = self.model.predict([cleaned])[0]
            prob_fraud = 1.0 if pred == 1 else 0.0

        label = "suspicious" if prob_fraud >= 0.50 else "legitimate"
        confidence_scaled = round(prob_fraud * 100.0, 2)
        top_features = self._extract_top_features_sklearn(cleaned)

        return MLPredictionOutput(
            label=label,
            probability=round(prob_fraud, 4),
            confidence_score=confidence_scaled,
            model_version=f"{self.algorithm.lower()}-{self.model_version}",
            algorithm=self.algorithm,
            top_features=top_features,
            decision_threshold=0.50,
        )

    def _extract_top_features_sklearn(self, text: str, max_features: int = 5) -> List[MLFeatureContribution]:
        """Extract tokens in the text with the strongest linear model weights."""
        if not self.model or not hasattr(self.model, "named_steps") or "tfidf" not in self.model.named_steps:
            return []

        try:
            tfidf = self.model.named_steps["tfidf"]
            clf = self.model.named_steps["clf"]

            if hasattr(clf, "coef_"):
                coefs = clf.coef_[0]
            elif hasattr(clf, "calibrated_classifiers_"):
                coefs = np.mean([cc.estimator.coef_[0] for cc in clf.calibrated_classifiers_], axis=0)
            else:
                return []

            feature_names = tfidf.get_feature_names_out()
            doc_vec = tfidf.transform([text]).toarray()[0]

            present_indices = np.where(doc_vec > 0)[0]
            if len(present_indices) == 0:
                return []

            contributions = []
            for idx in present_indices:
                token = feature_names[idx]
                token_weight = float(coefs[idx] * doc_vec[idx])
                contributions.append({
                    "token": token,
                    "weight": round(token_weight, 4),
                    "direction": "suspicious" if token_weight > 0 else "legitimate",
                })

            contributions.sort(key=lambda x: abs(x["weight"]), reverse=True)
            return [
                MLFeatureContribution(
                    token=c["token"],
                    weight=c["weight"],
                    direction=c["direction"],
                )
                for c in contributions[:max_features]
            ]
        except Exception as e:
            logger.debug(f"Could not extract token contributions: {e}")
            return []


# Global predictor instance
predictor = MLPredictor()

