"""core 包初始化：导出公共接口，触发 models/datasets 子包注册。"""

from .base import BaseModel, BaseDataset
from .registry import (
    register_model,
    register_dataset,
    get_model_class,
    get_dataset_class,
    list_models,
    list_datasets,
)
from .runner import run
from .llm_analyzer import LLMAnalyzer
from . import store

# 导入 models 和 datasets 包，触发 @register_model / @register_dataset
# 使用相对导入，不依赖顶层包名，重命名项目无需改动
from .. import models  # noqa: F401, E402
from .. import datasets  # noqa: F401, E402

__all__ = [
    "BaseModel",
    "BaseDataset",
    "register_model",
    "register_dataset",
    "get_model_class",
    "get_dataset_class",
    "list_models",
    "list_datasets",
    "run",
    "LLMAnalyzer",
    "store",
]
