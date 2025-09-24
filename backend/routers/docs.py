from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.responses import FileResponse
from typing import Dict, Any
from ..models.schemas import DocsIngestRequest, DocsGenerateRequest
from ..services import storage_service
from ..services import docs_service
import os
import tempfile


router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("/ingest")
async def ingest_curls(payload: DocsIngestRequest) -> Dict[str, Any]:
    project_dir = storage_service.get_project_dir(payload.project_id)
    if project_dir is None:
        raise HTTPException(status_code=404, detail="Project not found")

    parsed = docs_service.parse_curl_inputs(payload)
    storage_service.save_docs_inputs(payload.project_id, parsed)
    return {"ok": True, "endpoints": len(parsed.get("requests", []))}


@router.post("/generate")
async def generate_docs(payload: DocsGenerateRequest) -> Dict[str, Any]:
    project_dir = storage_service.get_project_dir(payload.project_id)
    if project_dir is None:
        raise HTTPException(status_code=404, detail="Project not found")

    inputs = storage_service.load_docs_inputs(payload.project_id)
    if not inputs:
        raise HTTPException(status_code=400, detail="No ingested cURL inputs found. Call /ingest first.")

    openapi_doc = docs_service.build_openapi_from_requests(
        project_name=payload.project_name or storage_service.load_project_metadata(payload.project_id).get("project_name") or payload.project_id,
        base_url_hint=payload.base_url,
        requests_payload=inputs.get("requests", []),
        ai_enabled=payload.ai_enabled,
    )
    md = docs_service.render_markdown_from_openapi(openapi_doc)

    storage_service.save_docs_openapi(payload.project_id, openapi_doc)
    storage_service.save_docs_markdown(payload.project_id, md)

    return {"ok": True, "paths": len(openapi_doc.get("paths", {}))}


@router.get("/openapi.json")
async def get_openapi(project_id: str):
    data = storage_service.load_docs_openapi(project_id)
    if not data:
        raise HTTPException(status_code=404, detail="No OpenAPI for project")
    return JSONResponse(content=data)


@router.get("/markdown", response_class=PlainTextResponse)
async def get_markdown(project_id: str):
    md = storage_service.load_docs_markdown(project_id)
    if md is None:
        raise HTTPException(status_code=404, detail="No Markdown for project")
    return md


@router.post("/generate-inline")
async def generate_docs_inline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OpenAPI + Markdown directly from provided cURL(s) without a project.

    Body supports:
    { "curls_text": "..." } or { "curls": ["curl ...", "curl ..."] }
    Optional: { "base_url": "https://api.example.com" }
    """
    parsed = docs_service.parse_curl_inputs(type("Obj", (), payload))  # simple adapter for existing fn
    requests = parsed.get("requests", [])
    if not requests:
        raise HTTPException(status_code=400, detail="No cURL commands provided")
    openapi_doc = docs_service.build_openapi_from_requests(
        project_name="Ad-hoc API",
        base_url_hint=payload.get("base_url"),
        requests_payload=requests,
        ai_enabled=True,
    )
    md = docs_service.render_markdown_from_openapi(openapi_doc, style=(payload.get("format") or payload.get("style") or "vendor"))
    return {"openapi": openapi_doc, "markdown": md}


@router.post("/export")
async def export_docs(payload: Dict[str, Any]):
    """Generate docs from cURL and return as a downloadable file.

    Body: { curls_text|curls, base_url?, format? (default), ai_enabled?, output: 'pdf'|'docx'|'md' }
    """
    parsed = docs_service.parse_curl_inputs(type("Obj", (), payload))
    requests = parsed.get("requests", [])
    if not requests:
        raise HTTPException(status_code=400, detail="No cURL commands provided")
    openapi_doc = docs_service.build_openapi_from_requests(
        project_name=payload.get("project_name") or "Generated API",
        base_url_hint=payload.get("base_url"),
        requests_payload=requests,
        ai_enabled=True,
    )
    style = (payload.get("format") or payload.get("style") or "vendor")
    md = docs_service.render_markdown_from_openapi(openapi_doc, style=style)
    output = (payload.get("output") or "pdf").lower()

    if output == "md":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as tmp:
            tmp.write(md)
            path = tmp.name
        fname = (openapi_doc.get("info", {}).get("title") or "api-docs").replace(' ', '-').lower() + ".md"
        return FileResponse(path, filename=fname, media_type="text/markdown")

    if output == "docx":
        try:
            path = docs_service.generate_docx(md)
            fname = (openapi_doc.get("info", {}).get("title") or "api-docs").replace(' ', '-').lower() + ".docx"
            return FileResponse(path, filename=fname, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX generation failed: {e}")

    # default PDF
    try:
        path = docs_service.generate_pdf(md)
        fname = (openapi_doc.get("info", {}).get("title") or "api-docs").replace(' ', '-').lower() + ".pdf"
        return FileResponse(path, filename=fname, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")


