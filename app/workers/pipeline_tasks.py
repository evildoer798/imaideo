from app.workers.celery_app import celery_app
from app.services.pipeline import run_project_pipeline
@celery_app.task(bind=True,max_retries=2)
def run_pipeline(self,project_id):
 try: return run_project_pipeline(project_id)
 except Exception as exc: raise self.retry(exc=exc, countdown=10)
