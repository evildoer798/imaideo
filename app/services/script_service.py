import re
from app.utils.file_parser import parse_script

def split_episodes(text:str):
 pattern=re.compile(r"(?im)^\s*(?:第\s*(\d+)\s*集|EP(?:ISODE)?\s*0*(\d+)|Episode\s+0*(\d+))\s*[:：】、.\s]*")
 matches=list(pattern.finditer(text))
 if not matches: return [(1,"EP01",text.strip())]
 result=[]
 for i,m in enumerate(matches):
  num=next(int(g) for g in m.groups() if g)
  body=text[m.end():(matches[i+1].start() if i+1<len(matches) else len(text))].strip()
  result.append((num,f"EP{num:02d}",body))
 return result

def analyze_story(text,episodes):
 names=[]
 for n in re.findall(r"(?m)^\s*([\u4e00-\u9fff]{2,8})\s*[：:]",text):
  if n not in names: names.append(n)
 for n in re.findall(r"\b([A-Z][A-Za-z0-9_]{1,20})\b",text):
  if n.upper() not in {"EP","EPISODE"} and n not in names: names.append(n)
 chars=[{"code":f"CHR{i:03d}","name":n,"age":None,"gender":"","role":"","appearance":{"identity_locked":True},"costumes":[],"personality":"","importance":"A"} for i,n in enumerate(names[:50],1)]
 scenes=[]
 for i,n in enumerate(re.findall(r"场景\s*[：:]\s*([^。\n]+)",text)):
  n=n.strip();
  if n and not any(s["name"]==n for s in scenes): scenes.append({"code":f"SCN{len(scenes)+1:03d}","name":n,"description":n,"layout":"","lighting":"","importance":"A"})
 return {"title":"AI Short Drama","genre":"short drama","visual_style":"cinematic","characters":chars,"scenes":scenes,"props":[],"timeline":[],"relationships":[]}
