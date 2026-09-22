"""LLM 抽象基类。"""

from abc import ABC, abstractmethod
from typing import List, Optional


class BaseLLM(ABC):
    """LLM 接口。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """模型名称。"""
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """同步对话接口，返回完整回复。"""
        raise NotImplementedError

    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """流式对话接口，默认退化为一次性返回。

        子类可覆写为真正的流式实现。
        """
        text = self.chat(system_prompt, user_prompt, temperature, max_tokens)
        yield text