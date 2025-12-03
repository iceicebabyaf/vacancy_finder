from sentence_transformers import util

from matcher.base_predictor import BasePredictor

class BertPredictor(BasePredictor):
    def __init__(self, model_type: str):
        super().__init__(model_type)
        self._setup_model()

    def __call__(self, profile: str, target: str) -> float:
        profile_emb = self.model.encode(profile, convert_to_tensor=True)
        target_emb = self.model.encode(target, convert_to_tensor=True)

        return util.cos_sim(profile_emb, target_emb)