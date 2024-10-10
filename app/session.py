import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.model import Base

load_dotenv()

class SessionConfig():
    def __init__(self):
        ...

    def url(self):
        if "SQLALCHEMY_DATABASE_URL" in os.environ:
            return os.environ["SQLALCHEMY_DATABASE_URL"]
        
        db_user = os.environ['DB_USER']
        db_pass = os.environ['DB_PASSWORD']
        db_host = os.environ['DB_HOST']
        db_port = os.environ['DB_PORT']
        db_name = os.environ['DB_NAME']
        return f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

session_config = SessionConfig()
engine = create_engine(session_config.url())
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()