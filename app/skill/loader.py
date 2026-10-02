from pathlib import Path
import hashlib
from app.config import get_settings
STAGES={"SCRIPT":["screenplay-gate-engine.md","dialogue-doctor-7d.md","dialogue-speed-check.md"],"ASSET":["asset-first-pipeline.md","asset-spatial-ledger.md","character-lineage-and-sheets.md"],"STORYBOARD":["spatial-topview-camera.md","camera-specs-15rules.md","camera-transitions-6types.md"],"VIDEO_PROMPT":["model-adapters.md","seedance-render-engine.md","segment-splicing.md","★ prompt-feeding-checklist.md"],"QC":["quality-gate-review.md"]}
class SkillLoader:
 def __init__(self,root=None,max_chars=None):
  s=get_settings(); self.root=Path(root or s.skill_root); self.max_chars=max_chars or s.skill_max_context_chars
 def load_stage(self,stage:str)->dict:
  names=["SKILL.md"]+STAGES.get(stage,[]); chunks=[]; loaded=[]
  for name in names:
   p=self.root/name if name=="SKILL.md" else self.root/"references"/name
   if p.exists(): chunks.append(f"\n# {name}\n"+p.read_text(encoding="utf-8",errors="ignore")); loaded.append(str(p))
  text="".join(chunks)[:self.max_chars]
  return {"stage":stage,"text":text,"files":loaded,"chars":len(text),"prompt_hash":hashlib.sha256(text.encode()).hexdigest()}
 def healthy(self): return (self.root/"SKILL.md").exists()
