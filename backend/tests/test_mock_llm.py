"""MockLLM 单元测试。"""

from app.services.llm.mock_llm import MockLLM


def test_mock_llm_with_context() -> None:
    llm = MockLLM()
    prompt = "【参考资料】\n[资料1] 企业知识库支持 Markdown 上传。\n\n【问题】\n支持什么上传？\n\n【回答】"
    answer = llm.chat("system", prompt)
    assert "Markdown" in answer
    assert "未在知识库中找到" not in answer


def test_mock_llm_without_context() -> None:
    llm = MockLLM()
    prompt = "【参考资料】\n无\n\n【问题】\n支持什么？\n\n【回答】"
    answer = llm.chat("system", prompt)
    assert "未在知识库中找到" in answer


def test_mock_llm_empty_prompt() -> None:
    llm = MockLLM()
    answer = llm.chat("system", "")
    assert "未在知识库中找到" in answer