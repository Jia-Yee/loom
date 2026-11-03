# 数据集文档

## diabetes（糖尿病数据集）

- **类型**：回归
- **注册名**：`diabetes`
- **来源**：sklearn.datasets.load_diabetes
- **样本数**：442
- **特征数**：10

### 特征列表

| 特征 | 说明 |
|------|------|
| age | 年龄（标准化） |
| sex | 性别 |
| bmi | 体重指数 |
| bp | 平均血压 |
| s1 | 血清测量 1（总胆固醇） |
| s2 | 血清测量 2（低密度脂蛋白） |
| s3 | 血清测量 3（高密度脂蛋白） |
| s4 | 血清测量 4（总胆固醇/HDL 比） |
| s5 | 血清测量 5（甘油三酯对数） |
| s6 | 血清测量 6（血糖） |

### 目标

疾病进展量化指标（连续值，范围 25-346）

### 特征与目标相关性 Top 5

| 特征 | 相关系数 |
|------|---------|
| bmi | 0.586 |
| s5 | 0.566 |
| bp | 0.441 |
| s4 | 0.430 |
| s3 | -0.395 |

---

## breast_cancer（乳腺癌数据集）

- **类型**：分类
- **注册名**：`breast_cancer`
- **来源**：sklearn.datasets.load_breast_cancer
- **样本数**：569
- **特征数**：30

### 特征概述

30 个特征分为 3 类，每类 10 个统计量（均值、标准误、最差值）：

- **半径**、**纹理**、**周长**、**面积**、**平滑度**、**紧凑度**、**凹度**、**凹点**、**对称性**、**分形维数**

### 目标

二分类：恶性（0）vs 良性（1）

### 类别分布

- 恶性：212（37.3%）
- 良性：357（62.7%）

### 使用示例

```python
from loom.core import run
result = run("logistic_regression", "breast_cancer")
# metrics: {"accuracy": 0.9649, "f1": 0.9647, "auc": 0.9954}
```

---

## california_housing（加州房价数据集）

- **类型**：回归
- **注册名**：`california_housing`
- **来源**：sklearn.datasets.fetch_california_housing
- **样本数**：20640
- **特征数**：8

### 特征列表

| 特征 | 说明 |
|------|------|
| MedInc | 街区收入中位数 |
| HouseAge | 房屋年龄中位数 |
| AveRooms | 平均房间数 |
| AveBedrms | 平均卧室数 |
| Population | 人口 |
| AveOccup | 平均入住率 |
| Latitude | 纬度 |
| Longitude | 经度 |

### 目标

加州房屋价格中位数（单位：十万美元）

---

## CSV 自定义数据集

通过 Web 控制台上传 CSV 文件，选择目标列和任务类型后自动注册。

### 上传流程

1. 在左侧面板点击「上传 CSV」
2. 选择文件，系统自动解析列名和预览数据
3. 选择目标列（target column）
4. 选择任务类型（回归/分类）
5. 注册后即可在数据集下拉框中选择

### 代码方式

```python
from loom.datasets.csv_loader import register_csv_dataset

register_csv_dataset(
    name="my_data",
    csv_path="data/my_data.csv",
    target_column="price",
    task_type="regression",
)

from loom.core import run
result = run("linear_regression", "my_data")
```
