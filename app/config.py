from functools import lru_cache
from pathlib import Path
try:
 from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
 class BaseSettings:
  def __init__(self, **kwargs):
   import os
   for k,v in self.__class__.__dict__.items():
    if not k.startswith("_") and not callable(v) and not isinstance(v, property): setattr(self,k,kwargs.get(k,os.getenv(k.upper(),v)))
 class SettingsConfigDict(dict):
  def __init__(self, **kwargs): super().__init__(**kwargs)
class Settings(BaseSettings):
    app_env: str = "development"; app_host: str = "0.0.0.0"; app_port: int = 8000; secret_key: str = "change-me"; database_url: str = "sqlite:///./shortdrama.db"; redis_url: str = "redis://localhost:6379/0"; storage_backend: str = "local"; storage_root: str = "./storage"; public_base_url: str = "http://localhost:8000"; llm_provider: str = "mock"; llm_base_url: str = ""; llm_api_key: str = ""; llm_model: str = ""; image_provider: str = "mock"; image_api_base_url: str = ""; image_api_key: str = ""; image_model: str = ""; video_provider: str = "mock"; ark_api_key: str = ""; seedance_model_id: str = ""; minimax_api_key: str = ""; minimax_video_model: str = "MiniMax-H3"; default_aspect_ratio: str = "9:16"; default_resolution: str = "720p"; skill_root: str = "./third_party/manju-laoli-skill/short-drama-director"; skill_max_context_chars: int = 24000; log_level: str = "INFO"; enable_paid_generation: bool = False; max_episodes_per_project: int = 50; max_shots_per_episode: int = 20; max_generation_retries: int = 2; episode_concurrency: int = 1; shot_concurrency: int = 2; auto_create_db: bool = True
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore",case_sensitive=False)
    @property
    def storage_path(self)->Path:
        p=Path(self.storage_root); p.mkdir(parents=True,exist_ok=True); return p
@lru_cache
def get_settings()->Settings: return Settings()
