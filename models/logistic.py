"""逻辑回归分类模型。"""

from sklearn.linear_model import LogisticRegression as _SkLogReg
import numpy as np

from ..core.base import BaseModel
from ..core.registry import register_model


@register_model("logistic_regression")
class LogisticRegressionModel(BaseModel):
    """sklearn LogisticRegression 包装。"""

    task_type = "classification"

    def __init__(self, **kwargs):
        kwargs.setdefault("max_iter", 5000)
        self._model = _SkLogReg(**kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {
            "C": self._model.C,
            "max_iter": self._model.max_iter,
            "solver": self._model.solver,
            "n_features_in_": getattr(self._model, "n_features_in_", None),
        }

    def param_space(self) -> dict:
        return {
            "C": [0.01, 0.1, 1.0, 10.0, 100.0],
            "solver": ["lbfgs", "liblinear"],
        }
