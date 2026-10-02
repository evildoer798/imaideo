import pytest
pytest.importorskip("sqlalchemy")
from pathlib import Path
from app.db.session import Base,engine,SessionLocal
from app.models.entities import Project
from app.services.pipeline import run_project_pipeline
def test_pipeline(tmp_path,monkeypatch):
 monkeypatch.setenv("STORAGE_ROOT",str(tmp_path)); Base.metadata.create_all(engine); db=SessionLocal(); p=Project(name="t",script_text="\u7b2c1\u96c6\n\u573a\u666f\uff1a\u5ba2\u5385\u3002\n\u5c0f\u660e\uff1a\u4f60\u597d\n\u7b2c2\u96c6\n\u573a\u666f\uff1a\u5b66\u6821\u3002\n\u5c0f\u7ea2\uff1a\u597d"); db.add(p); db.commit(); pid=p.id; db.close(); run_project_pipeline(pid); db=SessionLocal(); p=db.get(Project,pid); assert p.status.value=="COMPLETED"; assert len(p.episodes)==2; assert all(Path(e.final_video_path).exists() for e in p.episodes); db.close()
