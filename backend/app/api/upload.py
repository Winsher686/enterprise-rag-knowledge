"""文档上传接口。"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.logger import get_logger
from app.models.document import UploadResponse
from app.services.parser import get_parser
from app.services.splitter import get_splitter
from app.services.vectorstore import get_vector_store

logger = get_logger(__name__)

router = APIRouter(tags=["upload"])

_ALLOWED_EXTS = {".md", ".markdown", ".txt", ".pdf"}


@router.post("/upload", response_model=UploadResponse, summary="上传并解析文档")
async def upload_document(
    file: UploadFile = File(..., description="Markdown / TXT / PDF 文件"),
    title: str = Form(default="", description="可选文档标题"),
    prefer_mineru: bool = Form(default=False, description="PDF 是否优先使用 MinerU"),
    index: bool = Form(default=True, description="是否写入向量库"),
) -> UploadResponse:
    """上传文档，解析、切分，可选写入向量库。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = Path(file.filename).suffix.lower()
    if ext not in _ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{ext}，仅支持 {sorted(_ALLOWED_EXTS)}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parser = get_parser(tmp_path, prefer_mineru=prefer_mineru)
        document = parser.parse(tmp_path, title=title or None)
        document.source = file.filename

        splitter = get_splitter(file_type=document.file_type)
        chunks = splitter.split(document)

        if not chunks:
            raise HTTPException(status_code=400, detail="文档切分后为空")

        indexed = False
        if index:
            try:
                store = get_vector_store()
                store.add(chunks)
                indexed = True
            except Exception as exc:
                logger.warning("写入向量库失败：%s", exc)

        return UploadResponse(
            code=0,
            message="success",
            doc_id=document.doc_id,
            title=document.title,
            file_type=document.file_type,
            chunk_count=len(chunks),
            indexed=indexed,
            chunks=chunks,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("上传解析失败")
        raise HTTPException(status_code=500, detail=f"解析失败：{exc}") from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)