import os
from dataclasses import dataclass


@dataclass
class Settings:
    BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
    PROJECTS_DIR: str = os.path.join(DATA_DIR, "projects")
    SOPS_DIR: str = os.path.join(DATA_DIR, "sops")

    MODEL_BACKEND: str = os.getenv("MODEL_BACKEND", "none")  # hf | gpt4all | none
    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "google/flan-t5-base")
    GPT4ALL_MODEL_PATH: str = os.getenv("GPT4ALL_MODEL_PATH", os.path.join(DATA_DIR, "models", "ggml-gpt4all-j-v1.3-groovy.bin"))


settings = Settings()

# Ensure directories exist
for directory in (settings.DATA_DIR, settings.UPLOAD_DIR, settings.PROJECTS_DIR, settings.SOPS_DIR, os.path.dirname(settings.GPT4ALL_MODEL_PATH)):
    os.makedirs(directory, exist_ok=True)
