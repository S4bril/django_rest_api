from .knn_matcher import KNNMatcher
from .xgb_matcher import XGBMatcher


class MatcherFactory:
    @staticmethod
    def get_matcher(method="knn", **kwargs):
        if method == "knn":
            return KNNMatcher(features=["jaccard", "distance", "age_diff"])
        elif method == "xgb":
            model_path = kwargs.get("model_path", "match_model.xgb")
            return XGBMatcher(model_path=model_path)
        else:
            raise ValueError(f"Unknown matching method: {method}")
