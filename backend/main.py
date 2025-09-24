from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers.sop import router as sop_router
from .routers.docs import router as docs_router

app = FastAPI(title="SOP Generator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(sop_router, prefix="/api")
app.include_router(docs_router, prefix="/api")