import pandas as pd

# 1. 데이터 로드 (상가정보 CSV 파일 사용)
# 한글 데이터의 경우 인코딩(utf-8 또는 cp949) 처리가 필요합니다.
try:
    df_store = pd.read_csv("경주시 상가정보.csv", encoding='utf-8')
except UnicodeDecodeError:
    df_store = pd.read_csv("경주시 상가정보.csv", encoding='cp949')

df_region = pd.read_csv("20260907114845_지역별 방문자 수.csv", encoding='utf-8')

# 2. 관광 핵심 업종 필터링 및 결측치 제거
# 음식, 카페 등 라우팅의 목적지가 될 주요 상권만 추출 (대분류에 '음식'이 있다고 가정)
df_food = df_store[df_store['상권업종대분류명'] == '음식'].copy()

# 경로 탐색 알고리즘을 위해 위도, 경도, 행정동명이 없는 불량 데이터(결측치) 제거
df_food = df_food.dropna(subset=['경도', '위도', '행정동명'])

# 3. 핫플 vs 로컬 상권 라벨링 (동 단위 조인)
# 상가정보의 '행정동명'과 지역별 방문자 수의 '기초지자체명'을 기준으로 Left Join
df_merged = pd.merge(df_food, df_region, left_on='행정동명', right_on='기초지자체명', how='left')

# 조인되지 않은 지역(방문자 수 데이터가 없는 곳)의 방문자 비율은 0으로 채움
df_merged['기초지자체 방문자 비율'] = df_merged['기초지자체 방문자 비율'].fillna(0)

# 방문자 비율을 기준으로 핫플과 로컬 상권 분류
# (예시: 경주시 전체 방문자의 5% 이상이 몰리는 동은 '핫플레이스', 미만은 '로컬상권'으로 정의)
hotplace_threshold = 5.0
df_merged['상권분류'] = df_merged['기초지자체 방문자 비율'].apply(
    lambda x: '핫플레이스' if x >= hotplace_threshold else '로컬상권'
)

# 4. 라우팅 알고리즘 마스터 테이블 (Location Profile) 컬럼 정리
location_profile = df_merged[[
    '상가업소번호', '상호명', '상권업종중분류명', 
    '행정동명', '경도', '위도', 
    '기초지자체 방문자 비율', '상권분류'
]]

# 최종 결과 확인
print("--- Location Profile (POI 마스터 테이블) 미리보기 ---")
print(location_profile.head())

print("\n--- 상권분류별 장소 개수 ---")
print(location_profile['상권분류'].value_counts())

# 정제된 데이터를 새로운 CSV 파일로 저장
output_path = "DB_2_output.csv"
location_profile.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[성공] 정제된 데이터가 '{output_path}' 파일로 저장되었습니다.")