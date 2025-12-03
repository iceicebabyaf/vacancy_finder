from matcher.base_predictor import BasePredictor
from matcher.bert_predictor import BertPredictor

class Matcher:
    def __init__(self, model_type: str, profile: str, threshold=0.5):
        self.predictor: BasePredictor | None = None
        self.model_type = model_type
        self.profile = profile
        self.threshold = threshold

    def _setup_predictor(self) -> None:
        if self.model_type == "bert-l":
            self.predictor = BertPredictor(self.model_type)
        elif self.model_type == "word2vec-300":
            raise NotImplementedError("Word2vec model type is not implemented")

    def __call__(self, texts: list[tuple[int, str]]) -> dict[int, str]:
        results = {}

        for id, text in texts:
            results[id] = self.predictor(self.profile, text) > self.threshold

        return results