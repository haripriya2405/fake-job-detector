from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.ml.predictor import predictor
from app.ml.schemas import MLPredictionOutput


class AnalysisEngine(ABC):
    """Abstract interface for ML text analysis.
    Returns strictly machine-learning statistical predictions and feature attributions.
    Does NOT calculate final aggregated business risk scores.
    """

    @abstractmethod
    def analyze_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass


class DefaultAnalysisEngine(AnalysisEngine):
    """Real ML-integrated Analysis Engine.
    Produces purely ML-specific outputs (probability, confidence, top token weights, model version).
    Final risk score synthesis is explicitly delegated to the downstream RiskEngine.
    """

    def __init__(self):
        self.predictor = predictor

    def analyze_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.predictor.is_model_loaded():
            return {
                "status": "pending_model",
                "ml_label": "unassigned",
                "ml_probability": 0.0,
                "ml_confidence": 0.0,
                "model_version": "pending",
                "algorithm": "pending",
                "top_features": [],
                "engine_notice": "ML model artifact is pending training or loading.",
            }

        prediction: Optional[MLPredictionOutput] = self.predictor.predict(text)
        if not prediction:
            return {
                "status": "extraction_error",
                "ml_label": "unassigned",
                "ml_probability": 0.0,
                "ml_confidence": 0.0,
                "model_version": self.predictor.model_version,
                "algorithm": self.predictor.algorithm,
                "top_features": [],
                "engine_notice": "Could not extract predictive features from raw text.",
            }

        return {
            "status": "completed",
            "ml_label": prediction.label,
            "ml_probability": prediction.probability,
            "probability": prediction.probability,
            "ml_confidence": prediction.confidence_score,
            "model_version": prediction.model_version,
            "algorithm": prediction.algorithm,
            "top_features": [f.model_dump() for f in prediction.top_features],
            "highlight_spans": prediction.highlight_spans,
            "decision_threshold": prediction.decision_threshold,
            "engine_notice": (
                "ML statistical inference evaluated on calibrated NLP distribution. "
                "Raw probability is synthesized with deterministic security rules and domain verification."
            ),
        }


analysis_engine = DefaultAnalysisEngine()
