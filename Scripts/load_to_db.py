import pandas as pd
import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. 절대 경로로 BASE_DIR 추출 (Scripts 폴더의 상위 폴더인 DB_trip)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. 정확한 .env 파일 경로를 지정하여 로드
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

# DB 접속 정보 가져오기 (localhost 대신 127.0.0.1 사용 권장)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1") 
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
raw_password = os.getenv("DB_PASS")

# 3. 비밀번호에 특수문자(@, # 등)가 있을 경우를 대비해 URL 인코딩
if raw_password:
    DB_PASS = urllib.parse.quote_plus(raw_password)
else:
    DB_PASS = ""

# SQLAlchemy 엔진 생성
engine_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(engine_url)

def load_data():
    try:
        # 데이터 적재 코드 (이전과 동일)
        df1_path = os.path.join(BASE_DIR, "Data", "process", "DB_1_output.csv")
        if os.path.exists(df1_path):
            print(f"Loading {df1_path} to database...")
            df1 = pd.read_csv(df1_path)
            df1.to_sql('weather_visitor_spend', con=engine, if_exists='replace', index=False)
            print("Successfully loaded DB_1_output.csv to 'weather_visitor_spend' table.")
        else:
            print(f"Error: {df1_path} not found.")

        df2_path = os.path.join(BASE_DIR, "Data", "process", "DB_2_output.csv")
        if os.path.exists(df2_path):
            print(f"Loading {df2_path} to database...")
            df2 = pd.read_csv(df2_path)
            df2.to_sql('location_poi', con=engine, if_exists='replace', index=False)
            print("Successfully loaded DB_2_output.csv to 'location_poi' table.")
        else:
            print(f"Error: {df2_path} not found.")

    except Exception as e:
        print(f"An error occurred during data loading: {e}")

if __name__ == "__main__":
    load_data()