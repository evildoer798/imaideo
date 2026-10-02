from pathlib import Path
from app.config import get_settings
class StorageService:
 def __init__(self): self.root=get_settings().storage_path
 def project_path(self,project_id,*parts): p=self.root/"projects"/project_id; p.joinpath(*parts).parent.mkdir(parents=True,exist_ok=True); return p.joinpath(*parts)
 def save_bytes(self,project_id,relative,data): p=self.project_path(project_id,relative); p.write_bytes(data); return str(p)
