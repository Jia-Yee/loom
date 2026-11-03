"""注册表与查询接口。新增模型/数据集只需用装饰器注册，无需修改本文件。"""

from collections import defaultdict
from typing import Optional

from .base import BaseModel, BaseDataset

# 注册表：name → class
_MODEL_REGISTRY: dict[str, type[BaseModel]] = {}
_DATASET_REGISTRY: dict[str, type[BaseDataset]] = {}

# task_type 索引，加速 list_models(task_type=...) 查询
_MODEL_TASK_INDEX: dict[str, list[str]] = defaultdict(list)
_DATASET_TASK_INDEX: dict[str, list[str]] = defaultdict(list)


def register_model(name: str):
    """装饰器：注册模型类。

    用法：
        @register_model("linear_regression")
        class LinearRegressionModel(BaseModel): ...
    """

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        if name in _MODEL_REGISTRY:
            raise ValueError(f"模型 '{name}' 已注册")
        _MODEL_REGISTRY[name] = cls
        _MODEL_TASK_INDEX[cls.task_type].append(name)
        return cls

    return decorator


def register_dataset(name: str):
    """装饰器：注册数据集类。

    用法：
        @register_dataset("diabetes")
        class DiabetesDataset(BaseDataset): ...
    """

    def decorator(cls: type[BaseDataset]) -> type[BaseDataset]:
        if name in _DATASET_REGISTRY:
            raise ValueError(f"数据集 '{name}' 已注册")
        _DATASET_REGISTRY[name] = cls
        _DATASET_TASK_INDEX[cls.task_type].append(name)
        return cls

    return decorator


def get_model_class(name: str) -> type[BaseModel]:
    if name not in _MODEL_REGISTRY:
        raise KeyError(f"模型 '{name}' 未注册。可用: {list_models()}")
    return _MODEL_REGISTRY[name]


def get_dataset_class(name: str) -> type[BaseDataset]:
    if name not in _DATASET_REGISTRY:
        raise KeyError(f"数据集 '{name}' 未注册。可用: {list_datasets()}")
    return _DATASET_REGISTRY[name]


def list_models(task_type: Optional[str] = None) -> list[str]:
    """列出已注册模型名。可按 task_type 过滤。"""
    if task_type is None:
        return list(_MODEL_REGISTRY.keys())
    return list(_MODEL_TASK_INDEX.get(task_type, []))


def list_datasets(task_type: Optional[str] = None) -> list[str]:
    """列出已注册数据集名。可按 task_type 过滤。"""
    if task_type is None:
        return list(_DATASET_REGISTRY.keys())
    return list(_DATASET_TASK_INDEX.get(task_type, []))
