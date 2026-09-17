import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env 파일 로드 (backend 폴더 최상단에 .env가 있다고 가정)
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# SQLAlchemy 엔진 생성
engine_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(engine_url)

def get_db_engine():
    """데이터베이스 엔진을 반환하는 함수"""
    return engine