from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
import tempfile
import os
import asyncio

from mineru.cli.common import read_fn
from mineru.utils.enum_class import MakeMode
from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make

# 假如你还有其它自定义工具函数请补充import

app = FastAPI()

def run_sync_func_in_threadpool(func, *args, **kwargs):
    """通用封装：在异步接口里跑同步阻塞函数"""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, lambda: func(*args, **kwargs))

async def process_file(
    file_bytes: bytes,
    filename: str,
    backend: str = 'pipeline',
    file_type: str = 'pdf',
    lang: str = 'ch',
    server_url: Optional[str] = None
):
    """核心处理单个文件，返回分页markdown字符串列表"""
    parse_method = "auto"
    # 文件类型判断可自定义，这里统一为pdf图片都走一样流程
    pdf_bytes_list = [file_bytes]
    pdf_file_names = [Path(filename).stem]
    p_lang_list = [lang]

    # ========== pipeline 传统模型 ==========
    if backend == "pipeline":
        # 这是同步阻塞，需要用线程池包裹
        infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = await run_sync_func_in_threadpool(
            pipeline_doc_analyze, pdf_bytes_list, p_lang_list, parse_method, True, True
        )
        # 分页markdown
        markdown_pages = []
        for idx, model_list in enumerate(infer_results):
            images_list = all_image_lists[idx]
            pdf_doc = all_pdf_docs[idx]
            _lang = lang_list[idx]
            _ocr_enable = ocr_enabled_list[idx]
            middle_json = pipeline_result_to_middle_json(model_list, images_list, pdf_doc, None, _lang, _ocr_enable, True)
            pdf_info = middle_json["pdf_info"]
            page_md_list = pipeline_union_make(pdf_info, MakeMode.MM_MD, image_dir=None, return_page_list=True)
            markdown_pages.append(page_md_list)
        return markdown_pages[0]  # 单文件单条
    # ========== VLM 家族 ==========
    else:
        sub_backend = backend[4:] if backend.startswith("vlm-") else backend
        parse_method = "vlm"
        markdown_pages = []
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            # 用同步线程池保底，防 block
            middle_json, infer_result = await run_sync_func_in_threadpool(
                vlm_doc_analyze, pdf_bytes, None, sub_backend, server_url
            )
            pdf_info = middle_json["pdf_info"]
            page_md_list = vlm_union_make(pdf_info, MakeMode.MM_MD, image_dir=None, return_page_list=True)
            markdown_pages.append(page_md_list)
        return markdown_pages[0]

@app.post("/parse_pdf/", summary="上传文档转 markdown，含分页")
async def parse_pdf_endpoint(
    files: List[UploadFile] = File(..., description="上传文件，支持多个"),
    backend: str = Form('pipeline', description="处理后端类型（pipeline/vlm-xxx）"),
    file_type: str = Form('pdf', description="文件类型（pdf/png/jpg等）")
):
    result = []
    for file in files:
        file_bytes = await file.read()
        try:
            pages_markdown = await process_file(
                file_bytes, file.filename, backend=backend, file_type=file_type
            )
            result.append({
                "filename": file.filename,
                "pages": pages_markdown  # 每一页的 markdown 字符串
            })
        except Exception as ex:
            result.append({
                "filename": file.filename,
                "error": str(ex)
            })
    return JSONResponse(content={
        "results": result
    })