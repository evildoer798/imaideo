from pathlib import Path
from app.models.entities import *
from app.services.script_service import split_episodes,analyze_story
from app.services.storage_service import StorageService
from app.services.compose_service import ComposeService
from app.providers.video.mock import MockVideoProvider
from app.providers.video.base import CanonicalVideoRequest
from app.skill.loader import SkillLoader
from app.skill.validator import SkillValidator
from app.config import get_settings

def run_project_pipeline(project_id):
 db=SessionLocal(); storage=StorageService()
 try:
  project=db.get(Project,project_id)
  if not project or not project.script_text: raise ValueError("Project script is missing")
  project.status=ProjectStatus.PARSING; db.commit()
  parts=split_episodes(project.script_text)
  max_eps=project.settings.get("max_episode_count",get_settings().max_episodes_per_project)
  parts=parts[:max_eps]
  for num,title,body in parts:
   ep=db.query(Episode).filter_by(project_id=project.id,episode_number=num).first()
   if not ep: ep=Episode(project_id=project.id,episode_number=num,title=title,raw_script=body,normalized_script=body); db.add(ep)
  db.commit(); project.status=ProjectStatus.SCRIPT_PARSED; db.commit()
  story=analyze_story(project.script_text,parts); project.status=ProjectStatus.GLOBAL_ANALYSIS; db.commit()
  for c in story["characters"]:
   if not db.query(Character).filter_by(project_id=project.id,code=c["code"]).first(): db.add(Character(project_id=project.id,code=c["code"],name=c["name"],description=c["role"],appearance_json=c["appearance"],costume_json={"costumes":c["costumes"]},importance=c["importance"]))
  for s in story["scenes"]:
   if not db.query(Scene).filter_by(project_id=project.id,code=s["code"]).first(): db.add(Scene(project_id=project.id,code=s["code"],name=s["name"],description=s["description"],spatial_json=s))
  db.commit(); project.status=ProjectStatus.GLOBAL_ASSETS_PLANNED; db.commit()
  project.status=ProjectStatus.GLOBAL_ASSETS_GENERATING; db.commit()
  for c in db.query(Character).filter_by(project_id=project.id):
   for suffix in ("FRONT","SIDE","BACK","CLOSEUP"):
    code=f"{c.code}_{suffix}"
    if not db.query(Asset).filter_by(project_id=project.id,asset_code=code).first(): db.add(Asset(project_id=project.id,asset_type="character_"+suffix.lower(),entity_type="character",entity_id=c.id,asset_code=code,prompt=f"Locked reference for {c.code} {c.name}",status="LOCKED",file_path=storage.save_bytes(project.id,f"assets/{code}.txt",f"MOCK {code}".encode())))
  for s in db.query(Scene).filter_by(project_id=project.id):
   code=f"{s.code}_MASTER"
   if not db.query(Asset).filter_by(project_id=project.id,asset_code=code).first(): db.add(Asset(project_id=project.id,asset_type="scene_master",entity_type="scene",entity_id=s.id,asset_code=code,prompt=f"Locked master scene for {s.name}",status="LOCKED",file_path=storage.save_bytes(project.id,f"assets/{code}.txt",f"MOCK {code}".encode())))
  db.commit(); project.status=ProjectStatus.GLOBAL_ASSETS_READY; project.status=ProjectStatus.EPISODES_GENERATING; db.commit()
  validator=SkillValidator(); provider=MockVideoProvider(storage.root)
  for ep in db.query(Episode).filter_by(project_id=project.id).order_by(Episode.episode_number):
   if project.is_paused: break
   ep.status=EpisodeStatus.STORYBOARD_GENERATING; db.commit()
   lines=[x.strip() for x in ep.raw_script.splitlines() if x.strip()]
   lines=lines[:get_settings().max_shots_per_episode] or [ep.raw_script[:200]]
   shots=[]; storyboard=[]
   scenes=db.query(Scene).filter_by(project_id=project.id).all(); chars=db.query(Character).filter_by(project_id=project.id).all()
   for idx,line in enumerate(lines,1):
    code=f"EP{ep.episode_number:02d}_U{idx:02d}"; sh=db.query(Shot).filter_by(episode_id=ep.id,shot_code=code).first()
    if not sh: sh=Shot(episode_id=ep.id,shot_number=idx,shot_code=code,duration=2); db.add(sh); db.flush()
    refs=[a.asset_code for a in db.query(Asset).filter_by(project_id=project.id).limit(3).all()]
    sh.prompt=f"{code}: cinematic vertical shot, {line}, preserve locked assets {', '.join(refs)}"; sh.references_json=refs; sh.camera={"shot_size":"medium","angle":"eye-level","movement":"slow push-in"}; sh.status=ShotStatus.PROMPT_READY
    validator.validate(sh.prompt,project.target_model or "mock"); shots.append(sh); storyboard.append({"shot_id":code,"duration":2,"scene_code":scenes[0].code if scenes else None,"characters":[c.code for c in chars[:2]],"action":line,"reference_assets":refs})
   ep.storyboard_json={"episode_id":f"EP{ep.episode_number:02d}","shots":storyboard}; ep.status=EpisodeStatus.VIDEO_GENERATING; db.commit()
   for sh in shots:
    if sh.status==ShotStatus.DOWNLOADED: continue
    sh.status=ShotStatus.SUBMITTING; db.commit()
    task=GenerationTask(project_id=project.id,episode_id=ep.id,shot_id=sh.id,task_type="video",provider="mock",status="RUNNING",request_json={"prompt":sh.prompt}); db.add(task); db.commit()
    import asyncio
    result=asyncio.run(provider.create_task(CanonicalVideoRequest(sh.prompt,sh.duration,project.aspect_ratio)))
    sh.provider_task_id=result.provider_task_id; sh.local_video_path=str(storage.project_path(project.id,"episodes",f"EP{ep.episode_number:02d}","shots",f"{sh.shot_code}.mp4")); Path(result.result_url).replace(sh.local_video_path); sh.video_url=sh.local_video_path; sh.status=ShotStatus.DOWNLOADED; task.status="SUCCEEDED"; db.commit()
   ep.status=EpisodeStatus.COMPOSITING; db.commit(); ComposeService().compose_episode(ep,shots,storage); ep.status=EpisodeStatus.COMPLETED; db.commit()
  project.status=ProjectStatus.COMPLETED if not project.is_paused else ProjectStatus.EPISODES_GENERATING; db.commit()
 except Exception as exc:
  db.rollback(); project=db.get(Project,project_id)
  if project: project.status=ProjectStatus.FAILED; project.error_message=str(exc); db.commit()
 finally: db.close()

from app.db.session import SessionLocal
