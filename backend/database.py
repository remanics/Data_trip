import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env 파일 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# 핵심 해결 코드: 비밀번호의 @를 %40 등으로 안전하게 인코딩
encoded_pass = urllib.parse.quote_plus(DB_PASS) if DB_PASS else ""

# 인코딩된 비밀번호를 사용하여 엔진 URL 생성
engine_url = f"mysql+pymysql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(engine_url)

def get_db_engine():
    return engine