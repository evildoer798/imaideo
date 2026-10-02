from pydantic import BaseModel, Field
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=255); target_model:str|None=None; aspect_ratio:str="9:16"; style:str|None=None; language:str="zh-CN"
class ProjectOut(BaseModel): id:str; name:str; status:str; progress:dict; aspect_ratio:str; style:str|None; is_paused:bool
class StartOut(BaseModel): project_id:str; status:str; message:str
