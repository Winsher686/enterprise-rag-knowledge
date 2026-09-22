"""解析器单元测试。"""

from pathlib import Path

import pytest

from app.services.parser.simple_parser import SimpleParser


@pytest.fixture
def sample_md(tmp_path: Path) -> str:
    f = tmp_path / "sample.md"
    f.write_text("# 测试标题\n\n这是正文内容。", encoding="utf-8")
    return str(f)


def test_simple_parser_markdown(sample_md: str) -> None:
    parser = SimpleParser()
    doc = parser.parse(sample_md)
    assert doc.title == "测试标题"
    assert "这是正文内容" in doc.content
    assert doc.file_type == "md"


def test_simple_parser_unsupported(tmp_path: Path) -> None:
    f = tmp_path / "bad.docx"
    f.write_text("x", encoding="utf-8")
    parser = SimpleParser()
    with pytest.raises(ValueError):
        parser.parse(str(f))


def test_simple_parser_missing_file() -> None:
    parser = SimpleParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("not-exist.md")
