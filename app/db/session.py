from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.config import get_settings
class Base(DeclarativeBase): pass
s=get_settings(); connect_args={"check_same_thread":False} if s.database_url.startswith("sqlite") else {}
engine=create_engine(s.database_url,connect_args=connect_args,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=False)
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
