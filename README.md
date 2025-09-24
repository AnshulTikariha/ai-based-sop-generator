## SOP Generator

AI-assisted SOP and API documentation generator. Paste cURL to generate professional API docs (Markdown, PDF, DOCX) or upload a project to create SOPs. No third‑party keys required; uses local backends when available.

### Monorepo Structure
```
sop-generator/
  backend/     # FastAPI service (parsing, SOP generation, storage)
  frontend/    # React + Vite UI (upload, generate, view SOPs)
  demos/       # Sample demo projects (zip) for testing
```

---

## Backend (FastAPI)

- Language: Python 3.10+
- Frameworks/Libraries: FastAPI, Pydantic, Uvicorn

### Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run
```bash
source venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

API base: `http://127.0.0.1:8000/api`

### API Endpoints (SOP)

- GET `/sop/ai/backends` — list available AI backends
- POST `/sop/ai/backend` — set AI backend
  - body: `{ "backend": "hf" | "gpt4all" | "none", "hf_model_name"?: string, "gpt4all_model_path"?: string }`
- POST `/sop/upload` — upload a zip project
  - multipart form-data: `file: <project.zip>`
  - returns: `{ project_id, project_name }`
- POST `/sop/parse/{project_id}` — extract metadata from project
  - returns detected languages, frameworks, dependencies, routes
- POST `/sop/generate` — generate SOP
  - body:
```json
{
  "project_id": "string",
  "project_description": "Optional description",
  "template": {"sections": [{"title": "...", "content": "..."}]},
  "sop_style": "optional style"
}
```
- GET `/sop/list` — list generated SOPs
- GET `/sop/{sop_id}` — get SOP (JSON)
- GET `/sop/{sop_id}/markdown` — get SOP (markdown)
- DELETE `/sop/{sop_id}` — delete SOP

### API Endpoints (API Docs)

- POST `/api/docs/generate-inline` — Build OpenAPI and Markdown directly from pasted cURL
  - body: `{ "curls_text": "curl ...", "format": "vendor"|"sheet"|"default" }`
  - returns: `{ openapi, markdown }`
- POST `/api/docs/export` — Export API docs
  - body: `{ curls_text|curls, format: "vendor"|"sheet"|"default", output: "pdf"|"docx"|"md" }`
  - returns: file download; filename derived from API title

### Configuration

`backend/config.py` exposes runtime settings (e.g., model backend). Environment variables can override defaults as needed.

### Storage

Generated artifacts are written under `backend/data/`:
- `uploads/` — raw uploaded zips
- `projects/` — extracted projects
- `sops/` — generated SOPs (JSON and markdown)

---

## Frontend (React + Vite + TypeScript)

- UI to upload a project, trigger parsing and generation, and view/download SOPs
- Tech: React, React Router, TailwindCSS (with dark mode)

### Setup
```bash
cd frontend
npm install
```

### Run
```bash
npm run dev
```

By default the UI expects the backend on `http://127.0.0.1:8000/api`. Adjust `frontend/src/services/api.ts` or set `VITE_API_BASE`.

### API Docs Builder

1) Click “API Docs”. Paste cURL into the left panel.
2) Click “Generate Docs” to preview vendor-style documentation.
3) Use “Download PDF/DOCX” to export. Tables are full width with wrapping.

Notes:
- Headers are derived from cURL; sensitive values are masked.
- Request body JSON is parsed and a detailed “Request Body Fields” table is produced (nested objects supported).
- Descriptions can be AI-generated when local models are available, otherwise concise deterministic sentences are used.

### Build
```bash
npm run build
npm run preview
```

---

## Typical Workflow

1) Start backend (port 8000)
2) Start frontend (port 5173)
3) Either:
   - Upload a project zip → Parse → Generate SOP → View/Download
   - Or open API Docs → Paste cURL → Generate → Download PDF/DOCX

---

## Demos

Sample zips in `demos/` to try quickly:
- `node_express.zip`
- `python_fastapi.zip`
- `java_spring.zip` / `spring-crud.zip`

Upload any of these via the UI to generate an SOP immediately.

---

## Customization

- Templates: Provide `template.sections` in the SOP generate request to fully control output sections.
- AI Backend (SOP): Set to `hf`, `gpt4all`, or `none`. Docs generator uses deterministic text by default and can leverage local models for descriptions.

---

## Development Notes

- Code style: TypeScript/ESLint (frontend), Pydantic/FastAPI (backend)
- Dark mode supported via Tailwind class strategy
- Footer and navbar are defined in `frontend/src/routes/RootLayout.tsx`

---

## Troubleshooting

- Backend reload loops/Import errors: Check recent edits in `backend/services/*` for syntax/indentation.
- Port conflicts: Change ports with `--port` (backend) or `--port` in `npm run dev` (frontend).
- Large uploads: Ensure request size limits are sufficient (reverse proxy or dev server).
- Missing PDF/DOCX libs: ensure `reportlab` and `python-docx` are installed via backend/requirements.txt.

---

## License

MIT. Free for commercial and personal use. See notice in the footer and source headers where applicable.


