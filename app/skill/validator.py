import json,subprocess,sys
from pathlib import Path
class SkillValidator:
 def __init__(self,script=None): self.script=Path(script) if script else Path("third_party/manju-laoli-skill/short-drama-director/scripts/validate_prompt.py")
 def validate(self,prompt,model="mock"):
  if not prompt.strip(): return {"ok":False,"stdout":"","stderr":"empty prompt","return_code":1}
  if self.script.exists():
   try:
    r=subprocess.run([sys.executable,str(self.script),"--model",model,"--prompt",prompt],capture_output=True,text=True,timeout=20)
    return {"ok":r.returncode==0,"stdout":r.stdout,"stderr":r.stderr,"return_code":r.returncode}
   except Exception as e: return {"ok":False,"stdout":"","stderr":str(e),"return_code":1}
  return {"ok":True,"stdout":"offline validator","stderr":"","return_code":0}
