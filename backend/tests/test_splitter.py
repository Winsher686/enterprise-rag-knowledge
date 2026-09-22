"""切分器单元测试。"""

from app.models.document import Document
from app.services.splitter.markdown_splitter import MarkdownSplitter
from app.services.splitter.recursive_splitter import RecursiveCharacterSplitter


def _make_doc(content: str, title: str = "测试文档") -> Document:
    return Document(
        doc_id="test-doc-001",
        title=title,
        content=content,
        source="test.md",
        file_type="md",
    )


def test_recursive_splitter_short_text() -> None:
    splitter = RecursiveCharacterSplitter(chunk_size=100, chunk_overlap=20)
    result = splitter.split_text("这是一段很短的文本。")
    assert len(result) == 1


def test_recursive_splitter_long_text() -> None:
    splitter = RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=10)
    text = "第一句。" * 30
    result = splitter.split_text(text)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 100  # 允许一些 overlap 溢出


def test_markdown_splitter_headings() -> None:
    content = """# 主标题

## 第一节

第一节的内容。

## 第二节

第二节的内容。
"""
    doc = _make_doc(content)
    splitter = MarkdownSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split(doc)
    assert len(chunks) >= 2
    titles = {c.title for c in chunks}
    assert "第一节" in titles
    assert "第二节" in titles


def test_markdown_splitter_title_injection() -> None:
    content = "# 标题A\n\n内容A。\n\n# 标题B\n\n内容B。"
    doc = _make_doc(content)
    splitter = MarkdownSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split(doc)
    for chunk in chunks:
        assert chunk.content.startswith("文档来源：")
        assert chunk.title in chunk.content


def test_markdown_splitter_long_section() -> None:
    body = "这是一段很长的内容。" * 200
    content = f"# 长章节\n\n{body}"
    doc = _make_doc(content)
    splitter = MarkdownSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split(doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.title == "长章节"
