"""线性回归模型"""
from sklearn.linear_model import LinearRegression as _SkLinearRegression
import numpy as np
from ..core.base import BaseModel
from ..core.registry import register_model

@register_model("linear_regression")
class LinearRegressionModel(BaseModel):
    task_type = "regression"
    def __init__(self, **kwargs):
        self._model = _SkLinearRegression(**kwargs)
    def fit(self, X, y): self._model.fit(X, y)
    def predict(self, X): return self._model.predict(X)
    def get_params(self): return {"fit_intercept": self._model.fit_intercept}
    def param_space(self): return {"fit_intercept": [True, False]}
