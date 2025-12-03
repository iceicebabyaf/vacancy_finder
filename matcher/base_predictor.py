"""
Base predictor. Parent for predictors for all supported sentence matching models.
"""
from typing import Any

from sentence_transformers import SentenceTransformer, util

class BasePredictor:
    """Base predictor abstract class"""
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.model: Any | None = None

    def _setup_model(self) -> None:
        """Performs model setup."""
        if self.model_type == "bert-l":
            self.model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-tas-b")
        elif self.model_type == "word2vec-300":
            raise NotImplementedError("Word2vec model type is not implemented")

    def __call__(self, profile: str, target: str) -> float:
        """Performs matching of profile text string with target."""
        raise NotImplementedError("Matching is not implemented for this type of model.")