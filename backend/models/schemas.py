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
