from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import text
from app.api.router import router
from app.config import get_settings
from app.db.session import Base,engine,SessionLocal
from app import models
from app.skill.loader import SkillLoader
from app.utils.ffmpeg import ffmpeg_available
app=FastAPI(title="AI Short Drama Factory",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:3000"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(router)
@app.on_event("startup")
def startup():
 if get_settings().auto_create_db: Base.metadata.create_all(engine)
@app.get("/health")
def health():
 db="ok"
 try:
  with engine.connect() as c: c.execute(text("SELECT 1"))
 except Exception: db="error"
 return {"status":"ok" if db=="ok" else "degraded","database":db,"redis":"configured","ffmpeg":"ok" if ffmpeg_available() else "unavailable","skill":"ok" if SkillLoader().healthy() else "unavailable"}
@app.get("/storage/{path:path}")
def storage(path:str):
 p=Path(get_settings().storage_root)/path
 if not p.exists(): return {"detail":"Not found"}
 return FileResponse(p)
