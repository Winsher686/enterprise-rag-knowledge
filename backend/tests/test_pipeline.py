"""端到端流水线测试：解析 → 切分 → 入库 → 检索。"""

from pathlib import Path

import pytest

from app.models.document import Document
from app.services.splitter.markdown_splitter import MarkdownSplitter
from app.services.vectorstore.memory_store import MemoryVectorStore


@pytest.fixture
def sample_doc() -> Document:
    content = """# 企业知识库

## 文档上传

支持 Markdown 和 PDF 上传。

## 智能问答

用户可以用自然语言提问。

## 答案溯源

系统返回引用来源。
"""
    return Document(
        doc_id="pipeline-test",
        title="企业知识库",
        content=content,
        source="sample.md",
        file_type="md",
    )


def test_pipeline_end_to_end(sample_doc: Document) -> None:
    # 1. 切分
    splitter = MarkdownSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split(sample_doc)
    assert len(chunks) >= 2

    # 2. 入库
    store = MemoryVectorStore()
    store.clear()
    store.add(chunks)
    assert store.count() == len(chunks)

    # 3. 检索
    results = store.search("如何上传文档", top_k=3)
    assert len(results) > 0
    # 至少有一条结果包含"上传"或"文档"
    combined = " ".join(r.content for r in results)
    assert "上传" in combined or "文档" in combined