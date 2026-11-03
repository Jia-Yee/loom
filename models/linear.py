"""线性回归模型，包装 sklearn LinearRegression。"""

from sklearn.linear_model import LinearRegression as _SkLinearRegression
import numpy as np

from ..core.base import BaseModel
from ..core.registry import register_model


@register_model("linear_regression")
class LinearRegressionModel(BaseModel):
    """sklearn LinearRegression 包装。"""

    task_type = "regression"

    def __init__(self, **kwargs):
        self._model = _SkLinearRegression(**kwargs)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def get_params(self) -> dict:
        return {
            "fit_intercept": self._model.fit_intercept,
            "copy_X": self._model.copy_X,
            "n_features_in_": getattr(self._model, "n_features_in_", None),
            "coef": (
                self._model.coef_.tolist()
                if hasattr(self._model, "coef_")
                else None
            ),
            "intercept": (
                float(self._model.intercept_)
                if hasattr(self._model, "intercept_")
                else None
            ),
        }

    def param_space(self) -> dict:
        return {
            "fit_intercept": [True, False],
        }
