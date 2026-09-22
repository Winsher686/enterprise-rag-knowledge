"""Mock LLM：不依赖任何模型，基于 Prompt 中的参考资料生成答案。

规则：
- 如果 Prompt 中没有【参考资料】或参考资料为空，返回"未在知识库中找到依据"。
- 否则抽取参考资料的前若干内容拼接成答案。
支持按字符流式输出。
"""

import re
import time
from typing import Optional

from app.services.llm.base import BaseLLM

_NO_ANSWER = "未在知识库中找到相关依据，无法回答该问题。"


class MockLLM(BaseLLM):
    """Mock LLM。"""

    def __init__(self, max_snippet_chars: int = 600, stream_delay: float = 0.01) -> None:
        self._max_snippet_chars = max_snippet_chars
        self._stream_delay = stream_delay

    @property
    def name(self) -> str:
        return "mock-llm"

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        context = self._extract_context(user_prompt)
        if not context:
            return _NO_ANSWER

        snippet = context[: self._max_snippet_chars].strip()
        return f"根据知识库内容，回答如下：\n{snippet}"

    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """逐字符流式输出。"""
        text = self.chat(system_prompt, user_prompt, temperature, max_tokens)
        for ch in text:
            if self._stream_delay > 0:
                time.sleep(self._stream_delay)
            yield ch

    # ------------------------------------------------------------------
    @staticmethod
    def _extract_context(prompt: str) -> str:
        m = re.search(r"【参考资料】(.*?)(?:\n【|$)", prompt, re.DOTALL)
        if not m:
            return ""
        text = m.group(1).strip()
        if not text or text in ("无", "（无）"):
            return ""
        return text