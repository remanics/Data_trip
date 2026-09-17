import pandas as pd
from backend.database import get_db_engine

def get_location_data():
    """
    location_poi 테이블에서 공간 데이터를 불러옵니다.
    라우팅 알고리즘의 '노드(Node)' 및 '정적 가중치(핫플/로컬)'로 활용됩니다.
    """
    engine = get_db_engine()
    query = """
        SELECT 상가업소번호, 상호명, 상권업종중분류명, 행정동명, 경도, 위도, 상권분류 
        FROM location_poi
    """
    try:
        # SQL 쿼리 결과를 Pandas DataFrame으로 바로 읽어옵니다.
        df_location = pd.read_sql(query, con=engine)
        return df_location
    except Exception as e:
        print(f"공간 데이터 호출 중 오류 발생: {e}")
        return None

def get_daily_weather_and_visitor(target_date):
    """
    weather_visitor_spend 테이블에서 특정 날짜의 데이터를 불러옵니다.
    라우팅 알고리즘의 '동적 가중치(불쾌지수, 방문자 수)' 산출에 활용됩니다.
    
    :param target_date: int 형태의 날짜 (예: 20260701)
    """
    engine = get_db_engine()
    # 파라미터를 사용하여 SQL 인젝션을 방지하고 특정 날짜만 조회합니다.
    query = f"""
        SELECT 기준년월, 일일_방문자_수, 평균기온, 평균습도, 불쾌지수 
        FROM weather_visitor_spend 
        WHERE 기준년월 = {target_date}
    """
    try:
        df_status = pd.read_sql(query, con=engine)
        return df_status
    except Exception as e:
        print(f"시계열 데이터 호출 중 오류 발생: {e}")
        return None

# --- 테스트 실행 코드 ---
if __name__ == "__main__":
    # 공간 데이터 호출 테스트
    locations = get_location_data()
    if locations is not None:
        print("--- Location POI Data ---")
        print(locations.head())

    # 시계열 동적 데이터 호출 테스트 (예: 2026년 7월 1일)
    daily_status = get_daily_weather_and_visitor(20260701)
    if daily_status is not None:
        print("\n--- Daily Status Data (20260701) ---")
        print(daily_status)