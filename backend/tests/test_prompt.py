"""Prompt 构建测试。"""

from app.models.document import SearchResult
from app.services.prompt.rag_prompt import SYSTEM_PROMPT, build_user_prompt


def _make_ctx(cid: str, content: str) -> SearchResult:
    return SearchResult(
        chunk_id=cid,
        doc_id="doc-1",
        content=content,
        title="测试标题",
        score=0.9,
        metadata={"source": "test.md"},
    )


def test_build_prompt_with_contexts() -> None:
    contexts = [
        _make_ctx("c1", "内容A"),
        _make_ctx("c2", "内容B"),
    ]
    prompt = build_user_prompt("测试问题", contexts)
    assert "【参考资料】" in prompt
    assert "[资料1]" in prompt
    assert "[资料2]" in prompt
    assert "内容A" in prompt
    assert "内容B" in prompt
    assert "测试问题" in prompt


def test_build_prompt_without_contexts() -> None:
    prompt = build_user_prompt("测试问题", [])
    assert "【参考资料】" in prompt
    assert "无" in prompt
    assert "测试问题" in prompt


def test_system_prompt_rules() -> None:
    assert "不得编造" in SYSTEM_PROMPT
    assert "未在知识库中找到" in SYSTEM_PROMPT
    assert "引用资料编号" in SYSTEM_PROMPT