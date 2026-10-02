from fastapi import APIRouter,BackgroundTasks,Depends,File,HTTPException,UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import *
from app.schemas.api import ProjectCreate
from app.utils.file_parser import parse_script
from app.services.pipeline import run_project_pipeline
from app.config import get_settings
router=APIRouter(prefix="/api")
def progress(db,p):
 eps=db.query(Episode).filter_by(project_id=p.id).all(); assets=db.query(Asset).filter_by(project_id=p.id).count(); done=sum(e.status==EpisodeStatus.COMPLETED for e in eps)
 return {"global_assets":100 if assets else 0,"episodes_completed":done,"episodes_total":len(eps),"current_episode":next((e.episode_number for e in eps if e.status!=EpisodeStatus.COMPLETED),None)}
def project_dict(db,p): return {"id":p.id,"name":p.name,"status":p.status.value,"progress":progress(db,p),"aspect_ratio":p.aspect_ratio,"style":p.style,"is_paused":p.is_paused,"error_message":p.error_message}
@router.get("/projects")
def list_projects(db:Session=Depends(get_db)): return [project_dict(db,p) for p in db.query(Project).order_by(Project.created_at.desc()).all()]
@router.post("/projects")
def create_project(body:ProjectCreate,db:Session=Depends(get_db)):
 p=Project(name=body.name,target_model=body.target_model,aspect_ratio=body.aspect_ratio,style=body.style,language=body.language); db.add(p); db.commit(); db.refresh(p); return project_dict(db,p)
@router.get("/projects/{project_id}")
def get_project(project_id:str,db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p: raise HTTPException(404,"Project not found")
 d=project_dict(db,p); d["episodes"]=episodes(project_id,db); return d
@router.delete("/projects/{project_id}",status_code=204)
def delete_project(project_id:str,db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p: raise HTTPException(404,"Project not found")
 db.delete(p); db.commit()
@router.post("/projects/{project_id}/script")
async def upload_script(project_id:str,file:UploadFile=File(...),db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p: raise HTTPException(404,"Project not found")
 data=await file.read()
 try: text=parse_script(file.filename or "script.txt",data)
 except ValueError as e: raise HTTPException(400,str(e))
 path=get_settings().storage_path/"projects"/project_id/"source"/(file.filename or "script.txt"); path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
 p.original_filename=file.filename; p.script_path=str(path); p.script_text=text; p.status=ProjectStatus.UPLOADED; db.commit(); return {"project_id":project_id,"status":p.status.value,"characters":len(text)}
@router.post("/projects/{project_id}/start")
def start_project(project_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p or not p.script_text: raise HTTPException(400,"Upload a script first")
 bg.add_task(run_project_pipeline,project_id); return {"project_id":project_id,"status":"QUEUED","message":"Pipeline started"}
@router.post("/projects/{project_id}/retry")
def retry_project(project_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)):
 if not db.get(Project,project_id): raise HTTPException(404,"Project not found")
 bg.add_task(run_project_pipeline,project_id); return {"project_id":project_id,"status":"QUEUED"}
@router.post("/projects/{project_id}/pause")
def pause(project_id:str,db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p: raise HTTPException(404,"Project not found")
 p.is_paused=True; db.commit(); return project_dict(db,p)
@router.post("/projects/{project_id}/resume")
def resume(project_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)):
 p=db.get(Project,project_id)
 if not p: raise HTTPException(404,"Project not found")
 p.is_paused=False; db.commit(); bg.add_task(run_project_pipeline,project_id); return project_dict(db,p)
def episodes(project_id,db):
 return [{"id":e.id,"episode_number":e.episode_number,"title":e.title,"status":e.status.value,"final_video_path":e.final_video_path,"shots":len(e.shots)} for e in db.query(Episode).filter_by(project_id=project_id).order_by(Episode.episode_number)]
@router.get("/projects/{project_id}/episodes")
def project_episodes(project_id:str,db:Session=Depends(get_db)): return episodes(project_id,db)
@router.get("/projects/{project_id}/assets")
def project_assets(project_id:str,db:Session=Depends(get_db)): return [{"asset_code":a.asset_code,"asset_type":a.asset_type,"status":a.status,"file_path":a.file_path} for a in db.query(Asset).filter_by(project_id=project_id)]
@router.get("/episodes/{episode_id}")
def get_episode(episode_id:str,db:Session=Depends(get_db)):
 e=db.get(Episode,episode_id)
 if not e: raise HTTPException(404,"Episode not found")
 return {"id":e.id,"episode_number":e.episode_number,"title":e.title,"status":e.status.value,"storyboard":e.storyboard_json,"final_video_path":e.final_video_path,"shots":[shot_dict(s) for s in e.shots]}
@router.get("/episodes/{episode_id}/shots")
def episode_shots(episode_id:str,db:Session=Depends(get_db)): return [shot_dict(s) for s in db.query(Shot).filter_by(episode_id=episode_id).order_by(Shot.shot_number)]
@router.post("/episodes/{episode_id}/retry")
def retry_episode(episode_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)):
 e=db.get(Episode,episode_id)
 if not e: raise HTTPException(404,"Episode not found")
 bg.add_task(run_project_pipeline,e.project_id); return {"status":"QUEUED"}
def shot_dict(s): return {"id":s.id,"shot_code":s.shot_code,"duration":s.duration,"prompt":s.prompt,"status":s.status.value,"local_video_path":s.local_video_path}
@router.get("/shots/{shot_id}")
def get_shot(shot_id:str,db:Session=Depends(get_db)):
 s=db.get(Shot,shot_id)
 if not s: raise HTTPException(404,"Shot not found")
 return shot_dict(s)
@router.post("/shots/{shot_id}/retry")
def retry_shot(shot_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)):
 s=db.get(Shot,shot_id)
 if not s: raise HTTPException(404,"Shot not found")
 bg.add_task(run_project_pipeline,s.episode.project_id); return {"status":"QUEUED"}
@router.post("/shots/{shot_id}/regenerate")
def regenerate_shot(shot_id:str,bg:BackgroundTasks,db:Session=Depends(get_db)): return retry_shot(shot_id,bg,db)
@router.get("/generation-tasks/{task_id}")
def get_task(task_id:str,db:Session=Depends(get_db)):
 t=db.get(GenerationTask,task_id)
 if not t: raise HTTPException(404,"Task not found")
 return {"id":t.id,"status":t.status,"provider":t.provider,"response":t.response_json}
@router.post("/webhooks/seedance")
def seedance_webhook(payload:dict,db:Session=Depends(get_db)): return webhook(payload,db)
@router.post("/webhooks/minimax")
def minimax_webhook(payload:dict,db:Session=Depends(get_db)): return webhook(payload,db)
def webhook(payload,db):
 pid=payload.get("id") or payload.get("task_id")
 t=db.query(GenerationTask).filter_by(provider_task_id=pid).first() if pid else None
 if t: t.response_json=payload; t.status=payload.get("status","SUCCEEDED").upper(); db.commit()
 return {"ok":True}
