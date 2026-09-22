"""OpenAI 兼容接口 LLM 适配器（可调用 Qwen / vLLM / OpenAI 等）。

依赖 httpx，未配置 API Key 时由工厂自动降级为 MockLLM。
"""

from typing import List, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.services.llm.base import BaseLLM

logger = get_logger(__name__)


class OpenAICompatLLM(BaseLLM):
    """OpenAI Chat Completions 兼容接口。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("LLM_API_KEY 不能为空")
        if not base_url:
            raise ValueError("LLM_BASE_URL 不能为空")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return self._model

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        import httpx

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"解析 LLM 响应失败：{data}") from exc

    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """流式接口：SSE 解析。"""
        import httpx

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        with httpx.Client(timeout=self._timeout) as client:
            with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    if line == "[DONE]":
                        break
                    try:
                        import json
                        obj = json.loads(line)
                        delta = obj["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except Exception:
                        continue