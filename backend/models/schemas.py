from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SOPSection(BaseModel):
    title: str
    content: str


class SOPDocument(BaseModel):
    id: str
    project_name: str
    sections: List[SOPSection]
    metadata: Dict[str, Any]


class GenerateRequest(BaseModel):
    project_id: str
    project_description: Optional[str] = None
    template: Optional[Dict[str, Any]] = None
    sop_style: Optional[str] = None  # e.g., 'api_service', 'web_app', 'microservice', 'library', 'cli', 'data_pipeline'


class UploadResponse(BaseModel):
    project_id: str
    project_name: str
    message: str


class ListItem(BaseModel):
    id: str
    project_name: str
    modified_ts: float


class DocsIngestRequest(BaseModel):
    project_id: str
    curls_text: Optional[str] = None  # single text with one or many cURL commands
    curls: Optional[List[str]] = None  # array of individual curl commands


class DocsGenerateRequest(BaseModel):
    project_id: str
    project_name: Optional[str] = None
    base_url: Optional[str] = None
    ai_enabled: bool = True
