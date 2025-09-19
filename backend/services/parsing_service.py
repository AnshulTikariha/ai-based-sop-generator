import json
import os
import re
from typing import Dict, Any, List, Optional


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _read_text(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _maybe_project_root(project_dir: str) -> str:
    entries = [e for e in os.listdir(project_dir) if not e.startswith('.')]
    if len(entries) == 1:
        only = os.path.join(project_dir, entries[0])
        if os.path.isdir(only):
            return only
    return project_dir


def _find_first(project_dir: str, filename: str) -> Optional[str]:
    for root, _, files in os.walk(project_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None


def detect_language_and_framework(project_dir: str) -> Dict[str, Any]:
    project_dir = _maybe_project_root(project_dir)
    indicators: List[str] = os.listdir(project_dir)
    languages: List[str] = []
    frameworks: List[str] = []

    pkg_path = _find_first(project_dir, "package.json")
    if pkg_path:
        languages.append("JavaScript/TypeScript")
        pkg = _read_json(pkg_path) or {}
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if any(k in deps for k in ["react", "next", "vite"]):
            frameworks.append("React")
        if "express" in deps:
            frameworks.append("Express")
        if "vite" in deps:
            frameworks.append("Vite")

    reqs_path = _find_first(project_dir, "requirements.txt")
    pyproject = _find_first(project_dir, "pyproject.toml")
    if reqs_path or pyproject:
        languages.append("Python")
        reqs = _read_text(reqs_path) if reqs_path else None
        if reqs and re.search(r"fastapi|flask|django", reqs, re.IGNORECASE):
            if re.search(r"fastapi", reqs, re.IGNORECASE):
                frameworks.append("FastAPI")
            if re.search(r"flask", reqs, re.IGNORECASE):
                frameworks.append("Flask")
            if re.search(r"django", reqs, re.IGNORECASE):
                frameworks.append("Django")

    pom = _find_first(project_dir, "pom.xml")
    if pom:
        languages.append("Java")
        frameworks.append("Spring (possible)")

    docker = _find_first(project_dir, "Dockerfile")
    if docker:
        frameworks.append("Docker")

    return {"languages": list(set(languages)), "frameworks": list(set(frameworks))}


def parse_dependencies(project_dir: str) -> Dict[str, Any]:
    project_dir = _maybe_project_root(project_dir)
    data: Dict[str, Any] = {}
    pkg_path = _find_first(project_dir, "package.json")
    if pkg_path:
        pkg = _read_json(pkg_path) or {}
        data["node"] = {
            "name": pkg.get("name"),
            "version": pkg.get("version"),
            "dependencies": pkg.get("dependencies", {}),
            "devDependencies": pkg.get("devDependencies", {}),
            "scripts": pkg.get("scripts", {}),
        }
    reqs_path = _find_first(project_dir, "requirements.txt")
    if reqs_path:
        reqs = _read_text(reqs_path)
        if reqs:
            data["python"] = {"requirements": [line.strip() for line in reqs.splitlines() if line.strip() and not line.startswith("#")]}
    pom_path = _find_first(project_dir, "pom.xml")
    if pom_path:
        data["java"] = {"pom.xml": True}
    docker = _find_first(project_dir, "Dockerfile")
    if docker:
        data["docker"] = {"dockerfile": True}
    env_example_path = _find_first(project_dir, ".env.example")
    if env_example_path:
        data["env"] = {"example": _read_text(env_example_path)}
    return data


def extract_api_routes(project_dir: str) -> Dict[str, Any]:
    project_dir = _maybe_project_root(project_dir)
    routes: Dict[str, Any] = {}
    
    for root, _, files in os.walk(project_dir):
        for filename in files:
            full = os.path.join(root, filename)
            content = _read_text(full) or ""
            
            # FastAPI routes
            if filename.endswith(".py"):
                for match in re.finditer(r"@app\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", content):
                    method, path = match.group(1).upper(), match.group(2)
                    routes.setdefault("fastapi", []).append({"method": method, "path": path, "file": os.path.relpath(full, project_dir)})
            
            # Express routes
            if filename.endswith(".js") or filename.endswith(".ts"):
                for match in re.finditer(r"app\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", content):
                    method, path = match.group(1).upper(), match.group(2)
                    routes.setdefault("express", []).append({"method": method, "path": path, "file": os.path.relpath(full, project_dir)})
            
            # Spring Boot routes
            if filename.endswith(".java"):
                # Find @RequestMapping base path
                base_path = ""
                for match in re.finditer(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content):
                    base_path = match.group(1)
                
                # Find individual method mappings - match single line patterns
                for match in re.finditer(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)(?:\s*\(\s*["\']([^"\']+)["\']\s*\))?', content, re.MULTILINE):
                    method_annotation = match.group(1)
                    path = match.group(2) if match.group(2) else ""
                    
                    # Convert annotation to HTTP method
                    method_map = {
                        "GetMapping": "GET",
                        "PostMapping": "POST", 
                        "PutMapping": "PUT",
                        "DeleteMapping": "DELETE",
                        "PatchMapping": "PATCH"
                    }
                    http_method = method_map.get(method_annotation, "GET")
                    
                    # Combine base path with method path
                    if base_path and path:
                        full_path = base_path.rstrip("/") + "/" + path.lstrip("/")
                    elif base_path:
                        full_path = base_path
                    elif path:
                        full_path = path
                    else:
                        full_path = "/"
                    
                    if not full_path.startswith("/"):
                        full_path = "/" + full_path
                    
                    routes.setdefault("spring", []).append({
                        "method": http_method, 
                        "path": full_path, 
                        "file": os.path.relpath(full, project_dir)
                    })

            # Laravel routes (PHP)
            if filename.endswith(".php"):
                # Match Route::get('/path', ...) style definitions
                for match in re.finditer(r"Route::(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE):
                    method, path = match.group(1).upper(), match.group(2)
                    routes.setdefault("laravel", []).append({
                        "method": method,
                        "path": path,
                        "file": os.path.relpath(full, project_dir)
                    })
    
    return routes


def extract_project_metadata(project_dir: str) -> Dict[str, Any]:
    project_dir = _maybe_project_root(project_dir)
    info = detect_language_and_framework(project_dir)
    deps = parse_dependencies(project_dir)
    routes = extract_api_routes(project_dir)
    project_name = None
    if "node" in deps and deps["node"].get("name"):
        project_name = deps["node"]["name"]
    return {
        "project_name": project_name,
        "languages": info.get("languages", []),
        "frameworks": info.get("frameworks", []),
        "dependencies": deps,
        "routes": routes,
    }
