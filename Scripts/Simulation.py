import pandas as pd
import numpy as np

def run_roi_simulation():
    # 1. 시뮬레이션 고정 변수 (이 값들을 수정하며 테스트해 보세요!)
    daily_visitors = 320941        # 일평균 경주시 방문객 (데이터랩 기준)
    hot_place_ratio = 0.107        # 황남동(황리단길) 방문 비율 (10.7%)
    hot_place_visitors = daily_visitors * hot_place_ratio  # 하루 약 34,340명

    avg_local_spend = 15000        # 로컬상권 1인당 평균 예상 소비액 (원)
    coupon_value = 2000            # 우회 유도용 지역화폐/할인쿠폰 발행 금액 (원)

    # 2. 우회율 시나리오 설정 (5% ~ 30%까지 5% 단위)
    routing_rates = np.arange(0.05, 0.31, 0.05)

    results = []
    print("="*60)
    print(" [다이내믹 라우팅 로컬 상권 매출 상승 시뮬레이션] ")
    print(f" * 기준: 일평균 경주 방문객 {daily_visitors:,}명 | 황리단길 인파 {int(hot_place_visitors):,}명")
    print(f" * 조건: 쿠폰 {coupon_value:,}원 지급 시, 로컬 상권에서 {avg_local_spend:,}원 소비 가정")
    print("="*60 + "\n")

    # 3. 시나리오별 연산 로직
    for rate in routing_rates:
        routed_tourists = hot_place_visitors * rate               # 로컬로 이동한 관광객 수
        total_incentive_cost = routed_tourists * coupon_value     # 총 소요 예산
        gross_revenue = routed_tourists * avg_local_spend         # 로컬 상권 발생 매출
        net_revenue = gross_revenue - total_incentive_cost        # 순수 경제 효과
        roi = (net_revenue / total_incentive_cost) * 100          # 투자 대비 수익률(%)
        
        results.append({
            '우회율(%)': f"{int(rate * 100)}%",
            '이동 관광객': f"{int(routed_tourists):,}명",
            '투입 예산': f"{int(total_incentive_cost):,}원",
            '로컬 매출': f"{int(gross_revenue):,}원",
            '순수 경제효과': f"{int(net_revenue):,}원",
            'ROI': f"{int(roi)}%"
        })

    # 4. 결과 표 출력
    df_simulation = pd.DataFrame(results)
    print(df_simulation.to_string(index=False))
    print("\n" + "="*60)

if __name__ == "__main__":
    run_roi_simulation()