import os
import zipfile
from fastapi import UploadFile
from config import settings


def save_and_extract_zip(file: UploadFile, project_id: str) -> None:
    zip_path = os.path.join(settings.UPLOAD_DIR, f"{project_id}.zip")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(zip_path, "wb") as f:
        f.write(file.file.read())

    extract_dir = os.path.join(settings.PROJECTS_DIR, project_id)
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
