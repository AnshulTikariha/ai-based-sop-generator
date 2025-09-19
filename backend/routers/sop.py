from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import uuid
from typing import Dict, Any
from ..models.schemas import UploadResponse, GenerateRequest, SOPDocument, ListItem
from ..services import storage_service, parsing_service, ai_service
from ..utils.zip_utils import save_and_extract_zip

router = APIRouter(prefix="/sop", tags=["sop"])


@router.get("/ai/backends")
async def available_backends():
    return ai_service.list_available_backends()


@router.post("/ai/backend")
async def set_backend(payload: Dict[str, Any]):
    backend = payload.get("backend", "none")
    hf_model = payload.get("hf_model_name")
    gpt_path = payload.get("gpt4all_model_path")
    return ai_service.set_backend(backend, hf_model, gpt_path)


@router.post("/upload", response_model=UploadResponse)
async def upload_project(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")
    project_id = str(uuid.uuid4())
    project_name = file.filename[:-4]
    save_and_extract_zip(file, project_id)
    # Save initial metadata with project_name so later SOPs display a friendly name
    storage_service.save_project_metadata(project_id, {"project_name": project_name})
    return UploadResponse(project_id=project_id, project_name=project_name, message="Uploaded and extracted")


@router.post("/parse/{project_id}")
async def parse_project(project_id: str) -> Dict[str, Any]:
    project = storage_service.get_project_dir(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    metadata = parsing_service.extract_project_metadata(project)
    # Preserve an existing project_name if one was saved at upload time
    existing = storage_service.load_project_metadata(project_id) or {}
    if existing.get("project_name") and not metadata.get("project_name"):
        metadata["project_name"] = existing["project_name"]
    storage_service.save_project_metadata(project_id, metadata)
    return metadata


@router.post("/generate", response_model=SOPDocument)
async def generate_sop(request: GenerateRequest):
    project_dir = storage_service.get_project_dir(request.project_id)
    if project_dir is None:
        raise HTTPException(status_code=404, detail="Project not found")
    metadata = storage_service.load_project_metadata(request.project_id)
    sop = ai_service.generate_sop_document(
        project_id=request.project_id,
        project_name=metadata.get("project_name") or request.project_id,
        metadata=metadata,
        project_description=request.project_description,
        template=request.template,
    )
    storage_service.save_sop(sop)
    return sop


@router.get("/list", response_model=list[ListItem])
async def list_sops():
    return storage_service.list_sops()


@router.get("/{sop_id}", response_model=SOPDocument)
async def get_sop(sop_id: str):
    sop = storage_service.load_sop(sop_id)
    if sop is None:
        raise HTTPException(status_code=404, detail="SOP not found")
    return sop


@router.get("/{sop_id}/markdown", response_class=PlainTextResponse)
async def get_sop_markdown(sop_id: str):
    md = storage_service.load_sop_markdown(sop_id)
    if md is None:
        raise HTTPException(status_code=404, detail="SOP markdown not found")
    return md


@router.delete("/{sop_id}")
async def delete_sop(sop_id: str):
    removed = storage_service.delete_sop(sop_id)
    if not removed:
        raise HTTPException(status_code=404, detail="SOP not found")
    return {"ok": True}
