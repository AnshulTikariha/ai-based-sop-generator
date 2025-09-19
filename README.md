## SOP Generator

Generate professional, detailed SOP (Standard Operating Procedure) documents for uploaded code projects. The app analyzes project metadata and produces a structured SOP with tech stack, routes, commands, environment needs, and AI-enhanced insights.

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

### API Endpoints

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

By default the UI expects the backend on `http://127.0.0.1:8000/api`. Adjust `frontend/src/services/api.ts` if needed.

### Build
```bash
npm run build
npm run preview
```

---

## Typical Workflow

1) Start backend (port 8000)
2) Start frontend (port 5173)
3) In the UI, upload a project zip (or use one from `demos/`)
4) Parse project metadata
5) Generate SOP
6) View SOP as structured sections or download markdown

---

## Demos

Sample zips in `demos/` to try quickly:
- `node_express.zip`
- `python_fastapi.zip`
- `java_spring.zip` / `spring-crud.zip`

Upload any of these via the UI to generate an SOP immediately.

---

## Customization

- Templates: Provide `template.sections` in the generate request to fully control output sections.
- AI Backend: Set to `hf`, `gpt4all`, or `none`. When none, generation relies on rule-based content only.

---

## Development Notes

- Code style: TypeScript/ESLint (frontend), Pydantic/FastAPI (backend)
- Dark mode supported via Tailwind class strategy
- Footer and navbar are defined in `frontend/src/routes/RootLayout.tsx`

---

## Troubleshooting

- Backend reload loops/Import errors: Check recent edits in `backend/services/ai_service.py` for syntax/indentation.
- Port conflicts: Change ports with `--port` (backend) or `--port` in `npm run dev` (frontend).
- Large uploads: Ensure request size limits are sufficient (reverse proxy or dev server).

---

## License

MIT. Free for commercial and personal use. See notice in the footer and source headers where applicable.


