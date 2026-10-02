from pathlib import Path
from app.utils.ffmpeg import make_mock_video
from .base import ProviderTask
class MockVideoProvider:
 def __init__(self,root): self.root=Path(root)
 async def create_task(self,request):
  p=self.root/"mock"/(request.prompt[:24].replace(" ","_")+".mp4"); make_mock_video(p,request.prompt[:24],request.duration); return ProviderTask("mock-"+p.stem,"SUCCEEDED",str(p),{"mock":True})
 async def get_task(self,provider_task_id): return ProviderTask(provider_task_id,"SUCCEEDED")
