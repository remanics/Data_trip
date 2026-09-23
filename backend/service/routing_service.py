import osmnx as ox
import networkx as nx
import pandas as pd
from backend.services.data_service import get_location_data, get_daily_weather_and_visitor

class DynamicRoutingEngine:
    def __init__(self, target_date):
        # 1. 경주시 중심부(황리단길~성동시장) 도보 네트워크 로드
        self.center_point = (35.8385, 129.2082)
        print("경주시 도보 네트워크를 로드 중입니다...")
        self.graph = ox.graph_from_point(self.center_point, dist=1500, network_type='walk')
        
        # 2. DB에서 마스터 데이터 및 시계열 상태 데이터 호출
        self.locations = get_location_data()
        daily_status = get_daily_weather_and_visitor(target_date)
        
        # 오늘의 불쾌지수 추출 (데이터가 없으면 기본값 70 설정)
        self.today_thi = daily_status['불쾌지수'].iloc[0] if daily_status is not None else 70.0
        
        # 3. 노드에 핫플/로컬 속성 매핑을 위한 초기화
        self._map_pois_to_nodes()

    def _map_pois_to_nodes(self):
        """DB의 위경도 좌표를 도로망 네트워크의 가장 가까운 노드에 매핑합니다."""
        # 네트워크 노드의 위경도 리스트 추출
        nodes, _ = ox.graph_to_gdfs(self.graph)
        
        # 모든 노드의 초기 속성(핫플/로컬 여부)을 0으로 설정
        nx.set_node_attributes(self.graph, 0, 'is_hotplace')
        nx.set_node_attributes(self.graph, 0, 'is_local')

        if self.locations is not None:
            # DB 좌표를 OSM 노드 ID로 변환
            nearest_nodes = ox.distance.nearest_nodes(
                self.graph, 
                X=self.locations['경도'].values, 
                Y=self.locations['위도'].values
            )
            self.locations['nearest_node'] = nearest_nodes
            
            # 핫플 및 로컬 노드에 가중치 속성 부여
            for _, row in self.locations.iterrows():
                node = row['nearest_node']
                if row['상권분류'] == '핫플레이스':
                    self.graph.nodes[node]['is_hotplace'] += 1
                else:
                    self.graph.nodes[node]['is_local'] += 1

    def calculate_dynamic_weights(self, penalty_factor=2.0, local_incentive=50):
        """불쾌지수와 핫플/로컬 여부를 결합하여 다이내믹 가중치를 계산합니다."""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            base_distance = data.get('length', 1.0)
            
            # 해당 도로(Edge)의 도착지 노드(v)가 핫플인지 로컬인지 확인
            hotplace_count = self.graph.nodes[v].get('is_hotplace', 0)
            local_count = self.graph.nodes[v].get('is_local', 0)
            
            # 다이내믹 가중치 수식 적용
            # 불쾌지수(THI)가 높을수록 핫플을 지나갈 때 부여되는 패널티 거리가 기하급수적으로 증가함
            fatigue_penalty = hotplace_count * (self.today_thi * penalty_factor)
            reward_discount = local_count * local_incentive
            
            dynamic_weight = base_distance + fatigue_penalty - reward_discount
            
            # 다익스트라 알고리즘은 음수 간선을 허용하지 않으므로 최소값 1.0 보장
            data['dynamic_weight'] = max(1.0, dynamic_weight)

    def find_optimal_route(self, origin_coord, dest_coord):
        """출발지와 도착지 위경도를 입력받아 최적 우회 경로를 반환합니다."""
        # 출발지, 도착지 좌표를 가장 가까운 노드로 매핑
        orig_node = ox.distance.nearest_nodes(self.graph, X=origin_coord[1], Y=origin_coord[0])
        dest_node = ox.distance.nearest_nodes(self.graph, X=dest_coord[1], Y=dest_coord[0])
        
        # 가중치 계산 실행
        self.calculate_dynamic_weights()
        
        # 다이내믹 가중치를 바탕으로 한 다익스트라 최적 경로 탐색
        route_nodes = nx.shortest_path(
            self.graph, 
            orig_node, 
            dest_node, 
            weight='dynamic_weight'
        )
        
        return route_nodes

# --- 알고리즘 테스트 ---
if __name__ == "__main__":
    # 2026년 7월 1일 데이터를 기반으로 엔진 초기화
    routing_engine = DynamicRoutingEngine(target_date=20260701)
    
    # 임의의 출발지(신경주역 인근)와 도착지(동궁과 월지 인근) 위경도 설정
    origin = (35.8420, 129.2020)
    destination = (35.8340, 129.2210)
    
    optimal_route = routing_engine.find_optimal_route(origin, destination)
    print(f"\n최적 우회 경로 탐색 완료. 경로 노드 개수: {len(optimal_route)}개")