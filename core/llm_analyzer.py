"""LLM 调用封装：DeepSeek / Ollama，通过 OpenAI 兼容 SDK 统一调用。"""

import json
import os
from typing import Optional

from openai import OpenAI

# ── provider 默认配置 ──────────────────────────────────────
_PROVIDER_DEFAULTS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
    },
}


class LLMAnalyzer:
    """训练前数据分析 + 训练后结果解读。

    所有调用返回统一结构：
        {"content": str, "structured": dict|None, "parse_failed": bool}
    任何异常（网络/超时/密钥缺失）返回 None，主流程继续。
    """

    def __init__(self) -> None:
        self.provider = os.environ.get("AUTOML_LLM_PROVIDER", "").strip().lower()
        self.api_key = os.environ.get("AUTOML_LLM_API_KEY", "").strip()
        self.base_url = os.environ.get(
            "AUTOML_LLM_BASE_URL",
            _PROVIDER_DEFAULTS.get(self.provider, {}).get("base_url", ""),
        ).strip()
        self.model = os.environ.get(
            "AUTOML_LLM_MODEL",
            _PROVIDER_DEFAULTS.get(self.provider, {}).get("model", ""),
        ).strip()
        self.timeout = int(os.environ.get("AUTOML_LLM_TIMEOUT", "120"))

        self._client: Optional[OpenAI] = None
        self.last_error: str = ""
        if self.provider and self.base_url and self.model:
            # Ollama 不需要真实 key，但 SDK 要求非空
            key = self.api_key or ("ollama-placeholder" if self.provider == "ollama" else "")
            if key:
                self._client = OpenAI(
                    api_key=key, base_url=self.base_url, timeout=self.timeout
                )

    @property
    def available(self) -> bool:
        return self._client is not None

    # ── 公开方法 ────────────────────────────────────────────

    def analyze_data(self, data_summary: dict) -> Optional[dict]:
        """训练前数据分析。仅调用一次，所有模型共享。"""
        prompt = self._build_pre_train_prompt(data_summary)
        return self._call(prompt)

    def analyze_results(
        self, model_name: str, metrics: dict, data_summary: dict
    ) -> Optional[dict]:
        """训练后结果解读。按模型调用。"""
        prompt = self._build_post_train_prompt(model_name, metrics, data_summary)
        return self._call(prompt)

    # ── 内部方法 ────────────────────────────────────────────

    def _call(self, prompt: str) -> Optional[dict]:
        if not self.available:
            return None
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = resp.choices[0].message.content.strip()
            return self._parse(content)
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return None

    @staticmethod
    def _parse(content: str) -> dict:
        """尝试从 LLM 输出中提取 JSON，失败则保留原文。"""
        # 尝试直接解析
        try:
            return {"content": content, "structured": json.loads(content), "parse_failed": False}
        except json.JSONDecodeError:
            pass
        # 尝试提取 ```json ... ``` 块
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.index("```", start)
            snippet = content[start:end].strip()
            try:
                return {"content": content, "structured": json.loads(snippet), "parse_failed": False}
            except json.JSONDecodeError:
                pass
        # 纯文本
        return {"content": content, "structured": None, "parse_failed": True}

    @staticmethod
    def _build_pre_train_prompt(data_summary: dict) -> str:
        return (
            "你是一位数据科学顾问。请分析以下数据集摘要，给出：\n"
            "1. 适合的模型类型建议\n"
            "2. 潜在数据问题\n"
            "3. 对线性模型的适用性判断\n\n"
            "如果可能，请以 JSON 格式返回，包含字段：\n"
            '{"suggested_models": [...], "data_issues": [...], "linear_assessment": "..."}\n\n'
            f"数据集摘要：\n{json.dumps(data_summary, ensure_ascii=False, indent=2)}"
        )

    @staticmethod
    def _build_post_train_prompt(model_name: str, metrics: dict, data_summary: dict) -> str:
        return (
            "你是一位模型评估顾问。请解读以下训练结果，给出：\n"
            "1. 模型表现的自然语言解读\n"
            "2. 改进方向建议\n\n"
            "如果可能，请以 JSON 格式返回，包含字段：\n"
            '{"interpretation": "...", "improvement_suggestions": [...]}\n\n'
            f"模型：{model_name}\n"
            f"评估指标：{json.dumps(metrics, ensure_ascii=False)}\n"
            f"数据集摘要：{json.dumps(data_summary, ensure_ascii=False)}"
        )
