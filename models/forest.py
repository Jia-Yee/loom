"""随机森林回归模型，验证扩展性。"""

from sklearn.ensemble import RandomForestRegressor
import numpy as np

from ..core.base import BaseModel
from ..core.registry import register_model


@register_model("random_forest")
class RandomForestModel(BaseModel):
    """sklearn RandomForestRegressor 包装。"""

    task_type = "regression"

    def __init__(self, n_estimators: int = 100, max_depth: int | None = None, **kwargs):
        self._model = RandomForestRegressor(
            n_estimators=n_estimators, max_depth=max_depth, **kwargs
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {
            "n_estimators": self._model.n_estimators,
            "max_depth": self._model.max_depth,
            "n_features_in_": getattr(self._model, "n_features_in_", None),
        }

    def param_space(self) -> dict:
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 5, 10, 20],
        }
