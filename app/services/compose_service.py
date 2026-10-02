from pathlib import Path
from app.utils.ffmpeg import compose_videos
class ComposeService:
 def compose_episode(self,episode,shots,storage):
  inputs=[Path(s.local_video_path) for s in sorted(shots,key=lambda x:x.shot_number) if s.local_video_path]
  out=storage.project_path(episode.project_id,"episodes",f"EP{episode.episode_number:02d}",f"EP{episode.episode_number:02d}_final.mp4")
  compose_videos(inputs,out); episode.final_video_path=str(out); episode.duration=sum(s.duration for s in shots); return out
