"""示例：新增一个 Ridge 回归模型。"""

import numpy as np
from sklearn.linear_model import Ridge

from ..core.base import BaseModel
from ..core.registry import register_model


@register_model("ridge")
class RidgeModel(BaseModel):
    task_type = "regression"

    def __init__(self, alpha: float = 1.0, **kwargs):
        self._model = Ridge(alpha=alpha, **kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {
            "alpha": self._model.alpha,
            "solver": self._model.solver,
        }

    def param_space(self) -> dict:
        return {
            "alpha": [0.01, 0.1, 1.0, 10.0, 100.0],
        }
