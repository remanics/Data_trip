import pandas as pd

# 인코딩 혼합 문제 해결을 위한 코드 수정 (CP949로 된 파일과 UTF-8로 된 파일이 섞여 있음)
try:
    df_weather = pd.read_csv("경주시_날씨_데이터.csv", encoding='cp949')
except UnicodeDecodeError:
    df_weather = pd.read_csv("경주시_날씨_데이터.csv", encoding='utf-8')

try:
    df_visitor = pd.read_csv("20260907114843_방문자 수 추이.csv", encoding='utf-8')
except UnicodeDecodeError:
    df_visitor = pd.read_csv("20260907114843_방문자 수 추이.csv", encoding='cp949')

try:
    df_consume = pd.read_csv("20260907114616_관광소비 추이.csv", encoding='utf-8')
except UnicodeDecodeError:
    df_consume = pd.read_csv("20260907114616_관광소비 추이.csv", encoding='cp949')

# 기상 데이터 처리
df_weather['일시'] = pd.to_datetime(df_weather['일시'])
df_weather['기준년월'] = df_weather['일시'].dt.strftime('%Y%m%d').astype(int)

daily_weather = df_weather.groupby('기준년월').agg(
    평균기온=('기온(°C)', 'mean'),
    최고기온=('기온(°C)', 'max'),
    평균습도=('습도(%)', 'mean')
).reset_index()

T = daily_weather['평균기온']
H = daily_weather['평균습도'] / 100.0
daily_weather['불쾌지수'] = 1.8 * T - 0.55 * (1 - H) * (1.8 * T - 26) + 32

# 방문자 및 소비 데이터 필터링
df_visitor_tot = df_visitor[df_visitor['방문자 구분'] == '전체방문자(a+b)'][['기준년월', '방문자 수']]
df_visitor_tot.rename(columns={'방문자 수': '일일_방문자_수'}, inplace=True)

df_consume_tot = df_consume[df_consume['중분류'] == '관광총소비'][['기준년월', '소비액(천원)']]
df_consume_tot.rename(columns={'소비액(천원)': '일일_관광소비액'}, inplace=True)

# 병합
data_mart = pd.merge(df_visitor_tot, df_consume_tot, on='기준년월', how='inner')
data_mart = pd.merge(data_mart, daily_weather, on='기준년월', how='inner')

# 데이터 반올림
data_mart = data_mart.round(2)

# 정제된 데이터를 새로운 CSV 파일로 저장
output_path = "DB_1_output.csv"
data_mart.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[성공] 정제된 데이터가 '{output_path}' 파일로 저장되었습니다.")

print(data_mart.head())