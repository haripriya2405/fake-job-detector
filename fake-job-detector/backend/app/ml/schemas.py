from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MLFeatureContribution(BaseModel):
    token: str
    weight: float
    direction: str = "suspicious"  # "suspicious" | "legitimate"
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    context_sentence: Optional[str] = None


class MLPredictionOutput(BaseModel):
    label: str = Field(..., description="'suspicious' or 'legitimate'")
    probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated risk probability")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence scaled 0-100")
    model_version: str = Field(..., description="Unique model version identifier")
    algorithm: str = Field(..., description="Algorithm used (e.g. DeBERTa-v3-ONNX, LogisticRegression, CalibratedLinearSVM)")
    top_features: List[MLFeatureContribution] = Field(default_factory=list)
    highlight_spans: List[Dict[str, Any]] = Field(default_factory=list, description="Text spans identified as manipulative or high-risk")
    decision_threshold: float = 0.50
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelEvaluationMetrics(BaseModel):
    model_name: str
    version: str
    algorithm: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    confusion_matrix: List[List[int]]
    dataset_name: str
    train_samples: int
    val_samples: int
    test_samples: int
    classification_report: Dict[str, Any] = Field(default_factory=dict)
    false_positives: int
    false_negatives: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
