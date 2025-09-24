import json
import os
from typing import Optional, Dict, Any, List
from ..config import settings
from ..models.schemas import SOPDocument, SOPSection, ListItem


def get_project_dir(project_id: str) -> Optional[str]:
    candidate = os.path.join(settings.PROJECTS_DIR, project_id)
    return candidate if os.path.isdir(candidate) else None


def save_project_metadata(project_id: str, metadata: Dict[str, Any]) -> None:
    path = os.path.join(settings.PROJECTS_DIR, project_id, "metadata.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def load_project_metadata(project_id: str) -> Dict[str, Any]:
    path = os.path.join(settings.PROJECTS_DIR, project_id, "metadata.json")
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sop(sop: SOPDocument) -> None:
    json_path = os.path.join(settings.SOPS_DIR, f"{sop.id}.json")
    md_path = os.path.join(settings.SOPS_DIR, f"{sop.id}.md")
    os.makedirs(settings.SOPS_DIR, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sop.model_dump(), f, indent=2)
    from .ai_service import to_markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown(sop))


def load_sop(sop_id: str) -> Optional[SOPDocument]:
    path = os.path.join(settings.SOPS_DIR, f"{sop_id}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sections = [SOPSection(**s) for s in data.get("sections", [])]
    return SOPDocument(id=data["id"], project_name=data.get("project_name", data["id"]), sections=sections, metadata=data.get("metadata", {}))


def load_sop_markdown(sop_id: str) -> Optional[str]:
    path = os.path.join(settings.SOPS_DIR, f"{sop_id}.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_sops() -> List[ListItem]:
    items: List[ListItem] = []
    if not os.path.isdir(settings.SOPS_DIR):
        return items

    # Collect all SOPs
    all_sops: List[SOPDocument] = []
    for filename in os.listdir(settings.SOPS_DIR):
        if filename.endswith(".json"):
            sop = load_sop(filename[:-5])
            if sop:
                all_sops.append(sop)

    # De-duplicate by project_name, keep the most recent by file mtime
    latest_by_name: Dict[str, SOPDocument] = {}
    modified_ts_by_id: Dict[str, float] = {}
    for sop in all_sops:
        json_path = os.path.join(settings.SOPS_DIR, f"{sop.id}.json")
        mtime = os.path.getmtime(json_path)
        modified_ts_by_id[sop.id] = mtime
        key = sop.project_name
        prev = latest_by_name.get(key)
        if prev is None:
            latest_by_name[key] = sop
        else:
            prev_mtime = os.path.getmtime(os.path.join(settings.SOPS_DIR, f"{prev.id}.json"))
            if mtime >= prev_mtime:
                latest_by_name[key] = sop

    for sop in latest_by_name.values():
        items.append(ListItem(id=sop.id, project_name=sop.project_name, modified_ts=modified_ts_by_id.get(sop.id, 0.0)))

    # Sort alphabetically by project_name
    # Sort alphabetically for stability, but the frontend computes latest by timestamp
    items.sort(key=lambda x: x.project_name.lower())
    return items


def delete_sop(sop_id: str) -> bool:
    """Delete SOP(s).

    If the SOP with `sop_id` exists, we also delete all other SOPs that
    share the same `project_name`. This matches the UI which shows only
    one card per project (latest), so deleting it should remove the
    project from the list entirely.
    """
    target = load_sop(sop_id)
    removed = False

    # If we know the project_name, remove all SOPs that share it
    if target is not None:
        project_name = target.project_name
        if os.path.isdir(settings.SOPS_DIR):
            for filename in os.listdir(settings.SOPS_DIR):
                if not filename.endswith('.json'):
                    continue
                sop = load_sop(filename[:-5])
                if sop and sop.project_name == project_name:
                    json_path = os.path.join(settings.SOPS_DIR, f"{sop.id}.json")
                    md_path = os.path.join(settings.SOPS_DIR, f"{sop.id}.md")
                    if os.path.isfile(json_path):
                        os.remove(json_path)
                        removed = True
                    if os.path.isfile(md_path):
                        os.remove(md_path)
                        removed = True
        return removed

    # Fallback: delete by id only
    json_path = os.path.join(settings.SOPS_DIR, f"{sop_id}.json")
    md_path = os.path.join(settings.SOPS_DIR, f"{sop_id}.md")
    if os.path.isfile(json_path):
        os.remove(json_path)
        removed = True
    if os.path.isfile(md_path):
        os.remove(md_path)
        removed = True
    return removed


# ----------------------
# API Docs persistence
# ----------------------

def _docs_dir(project_id: str) -> str:
    return os.path.join(settings.PROJECTS_DIR, project_id, "docs")


def save_docs_inputs(project_id: str, data: Dict[str, Any]) -> None:
    path = os.path.join(_docs_dir(project_id), "inputs.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_docs_inputs(project_id: str) -> Dict[str, Any] | None:
    path = os.path.join(_docs_dir(project_id), "inputs.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_docs_openapi(project_id: str, openapi: Dict[str, Any]) -> None:
    path = os.path.join(_docs_dir(project_id), "openapi.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(openapi, f, indent=2)


def load_docs_openapi(project_id: str) -> Dict[str, Any] | None:
    path = os.path.join(_docs_dir(project_id), "openapi.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_docs_markdown(project_id: str, md: str) -> None:
    path = os.path.join(_docs_dir(project_id), "docs.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)


def load_docs_markdown(project_id: str) -> str | None:
    path = os.path.join(_docs_dir(project_id), "docs.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
