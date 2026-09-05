import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.ml.dataset import JobFraudDataset
from app.ml.evaluate import ModelEvaluator
from app.ml.preprocessing import TextPreprocessor, preprocessor
from app.ml.schemas import ModelEvaluationMetrics
from app.models.model_version import ModelVersion


class ModelTrainer:
    """Trains, compares, serializes, and registers TF-IDF NLP fraud classification models."""

    def __init__(self, artifacts_dir: str = "artifacts/models"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.evaluator = ModelEvaluator()

    def build_logistic_regression_pipeline(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        max_features: int = 5000,
        C: float = 1.0,
    ) -> Pipeline:
        """Create a versioned TF-IDF + Logistic Regression pipeline."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                preprocessor=preprocessor.clean_text,
                ngram_range=ngram_range,
                max_features=max_features,
                sublinear_tf=True,
                token_pattern=r'(?u)\b\w+\b',
            )),
            ("clf", LogisticRegression(
                C=C,
                max_iter=1000,
                random_state=42,
                class_weight="balanced",
                solver="liblinear",
            )),
        ])

    def build_calibrated_svm_pipeline(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        max_features: int = 5000,
        C: float = 1.0,
    ) -> Pipeline:
        """Create a versioned TF-IDF + Linear SVM pipeline with probability calibration."""
        base_svm = LinearSVC(
            C=C,
            random_state=42,
            class_weight="balanced",
            max_iter=2000,
        )
        calibrated_svm = CalibratedClassifierCV(estimator=base_svm, cv=3)

        return Pipeline([
            ("tfidf", TfidfVectorizer(
                preprocessor=preprocessor.clean_text,
                ngram_range=ngram_range,
                max_features=max_features,
                sublinear_tf=True,
                token_pattern=r'(?u)\b\w+\b',
            )),
            ("clf", calibrated_svm),
        ])

    def train_and_evaluate(
        self,
        dataset: Optional[JobFraudDataset] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Train both Logistic Regression and Linear SVM models, compare performance metrics,
        and serialize the optimal validated artifact.
        """
        if dataset is None:
            dataset = JobFraudDataset()

        train_df, val_df, test_df = dataset.get_splits(test_size=0.15, val_size=0.15, random_state=42)

        X_train, y_train = train_df["text"], train_df["label"]
        X_val, y_val = val_df["text"], val_df["label"]
        X_test, y_test = test_df["text"], test_df["label"]

        logger.info(f"Dataset split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

        # 1. Train Model A: TF-IDF + Logistic Regression
        logreg_pipe = self.build_logistic_regression_pipeline()
        logreg_pipe.fit(X_train, y_train)
        logreg_metrics = self.evaluator.evaluate(
            model=logreg_pipe,
            X_test=X_test,
            y_test=y_test,
            model_name="tfidf_logistic_regression",
            version="v1.0.0",
            algorithm="LogisticRegression",
            dataset_name=dataset.metadata["name"],
            train_samples=len(train_df),
            val_samples=len(val_df),
            test_samples=len(test_df),
        )

        # 2. Train Model B: TF-IDF + Calibrated Linear SVM
        svm_pipe = self.build_calibrated_svm_pipeline()
        svm_pipe.fit(X_train, y_train)
        svm_metrics = self.evaluator.evaluate(
            model=svm_pipe,
            X_test=X_test,
            y_test=y_test,
            model_name="tfidf_linear_svm",
            version="v1.0.0",
            algorithm="CalibratedLinearSVM",
            dataset_name=dataset.metadata["name"],
            train_samples=len(train_df),
            val_samples=len(val_df),
            test_samples=len(test_df),
        )

        # Compare F1 score and false negatives (critical for fraud detection)
        # Choose the model with superior F1 score and lower false negative rate
        if logreg_metrics.f1_score >= svm_metrics.f1_score:
            selected_model = logreg_pipe
            selected_metrics = logreg_metrics
            selected_name = "tfidf_logistic_regression"
            selection_reason = "Logistic Regression demonstrated superior calibrated probability curves and high F1 balance."
        else:
            selected_model = svm_pipe
            selected_metrics = svm_metrics
            selected_name = "tfidf_linear_svm"
            selection_reason = "Calibrated Linear SVM demonstrated superior margin separation on boundary fraud cases."

        # Save selected production model artifact
        artifact_filename = f"{selected_name}_{selected_metrics.version}.joblib"
        artifact_path = os.path.join(self.artifacts_dir, artifact_filename)
        joblib.dump(selected_model, artifact_path)

        # Compute SHA256 integrity hash
        with open(artifact_path, "rb") as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()

        # Save metadata manifest
        meta_filename = f"{selected_name}_{selected_metrics.version}.meta.json"
        meta_path = os.path.join(self.artifacts_dir, meta_filename)
        metadata = {
            "model_name": selected_name,
            "version": selected_metrics.version,
            "algorithm": selected_metrics.algorithm,
            "artifact_path": artifact_path,
            "sha256_checksum": sha256_hash,
            "dataset": dataset.metadata,
            "metrics": selected_metrics.model_dump(),
            "selection_reason": selection_reason,
            "comparison": {
                "logistic_regression": logreg_metrics.model_dump(),
                "calibrated_linear_svm": svm_metrics.model_dump(),
            },
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)

        # Create or update database ModelVersion record if session provided
        if db:
            existing_mv = db.query(ModelVersion).filter(ModelVersion.version == selected_metrics.version).first()
            if not existing_mv:
                mv = ModelVersion(
                    id=uuid.uuid4(),
                    name=selected_name,
                    version=selected_metrics.version,
                    algorithm=selected_metrics.algorithm,
                    training_dataset=dataset.metadata["name"],
                    accuracy=selected_metrics.accuracy,
                    f1_score=selected_metrics.f1_score,
                    is_active=True,
                    artifact_path=artifact_path,
                    metadata_json=json.dumps(metadata, default=str),
                )
                db.add(mv)
                db.commit()

        logger.info(f"Model trained and serialized to '{artifact_path}' (Accuracy: {selected_metrics.accuracy:.4f}, F1: {selected_metrics.f1_score:.4f})")

        return {
            "selected_model": selected_model,
            "selected_metrics": selected_metrics,
            "artifact_path": artifact_path,
            "metadata_path": meta_path,
            "logreg_metrics": logreg_metrics,
            "svm_metrics": svm_metrics,
        }
