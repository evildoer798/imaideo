from dataclasses import dataclass,field
from typing import Protocol
@dataclass
class CanonicalVideoRequest: prompt:str; duration:int=2; aspect_ratio:str="9:16"; resolution:str|None="720p"; reference_images:list[str]=field(default_factory=list); reference_videos:list[str]=field(default_factory=list); reference_audio:list[str]=field(default_factory=list); first_frame:str|None=None; last_frame:str|None=None; callback_url:str|None=None
@dataclass
class ProviderTask: provider_task_id:str; status:str; result_url:str|None=None; raw:dict=field(default_factory=dict)
class VideoProvider(Protocol):
 async def create_task(self,request:CanonicalVideoRequest)->ProviderTask: ...
