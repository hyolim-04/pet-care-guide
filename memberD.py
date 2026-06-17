import json
import math
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from flask import Blueprint, jsonify, request, send_from_directory

bp_d = Blueprint('memberD', __name__, template_folder='static')


# [외부 API] 카카오모빌리티 Directions API 엔드포인트
# - 차량 최단거리/최단시간 경로 계산에 사용
# - 실제 추천 순위 계산은 아래의 Graph + Min-Heap + Top-K 알고리즘에서 수행
KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


@bp_d.route("/memberD")
def member_d_page():
    return send_from_directory("static", "memberD.html")


# ==============================================================================
# 1. 자료구조: 그래프 (Graph)
# - 내 위치(origin)와 병원을 노드(Node)로 저장
# - 내 위치에서 각 병원까지의 이동 비용을 가중치 간선(Weighted Edge)으로 저장
# - 인접 간선 기반 후보 탐색 알고리즘의 핵심 입력 데이터
# - 시간 복잡도:
#   · 노드 추가/갱신: O(V) — V: 전체 노드 수
#   · 간선 추가: O(1)
#   · 특정 출발 노드의 간선 조회: O(E) — E: 전체 간선 수
# ==============================================================================

# [자료구조] 그래프 (Graph)
# - nodes: 장소 정보를 담는 동적 배열(List)
# - edges: 출발 노드, 도착 노드, 가중치를 담는 동적 배열(List)
class HospitalGraph:
    def __init__(self):
        self.nodes = []   # [자료구조] 동적 배열(List) — origin과 병원 노드 저장
        self.edges = []   # [자료구조] 동적 배열(List) — origin -> 병원 가중치 간선 저장

    # [알고리즘] 노드 삽입/갱신
    # - 같은 id의 노드가 이미 있으면 병원 거리/시간 정보를 최신 값으로 갱신
    # - 없으면 새 노드로 추가
    def add_node(self, node):
        for i, item in enumerate(self.nodes):
            if item.get("id") == node.get("id"):
                self.nodes[i] = {**item, **node}
                return
        self.nodes.append(node)

    # [알고리즘] 가중치 간선 추가
    # - from_id에서 to_id까지 이동 비용(weight)을 저장
    # - weight는 거리 기준이면 미터, 시간 기준이면 초 단위
    def add_edge(self, from_id, to_id, weight, meta=None):
        self.edges.append(
            {"from": from_id, "to": to_id, "weight": weight, **(meta or {})}
        )

    # [알고리즘] 노드 선형 탐색
    # - 노드 id로 병원 정보를 조회
    # - 시간 복잡도: O(V)
    def get_node(self, node_id):
        for node in self.nodes:
            if node.get("id") == node_id:
                return node
        return None

    # [알고리즘] 병원 노드 필터링
    # - 전체 노드 중 type == "hospital"인 노드만 추출
    def get_hospitals(self):
        return [node for node in self.nodes if node.get("type") == "hospital"]

    # [알고리즘] 인접 간선 조회
    # - 특정 노드에서 출발하는 간선만 필터링
    # - 본 프로젝트에서는 origin에서 각 병원으로 이어지는 후보 간선 조회에 사용
    def get_edges_from(self, node_id):
        return [edge for edge in self.edges if edge.get("from") == node_id]


# ==============================================================================
# 2. 자료구조: 우선순위 큐 (Priority Queue / Min-Heap)
# - 병원 후보를 이동 비용(dist)이 낮은 순서대로 꺼내기 위한 자료구조
# - 내부적으로 배열(List)을 완전 이진 트리처럼 사용
# - push/pop 시간 복잡도: O(log N) — N: 힙에 들어간 후보 병원 수
# - Top-K 선택 알고리즘의 핵심 자료구조
# ==============================================================================

# [자료구조] 최소 힙 (Min-Heap)
# - heap[0]에 항상 가장 낮은 비용의 병원 후보가 위치
class MinHeap:
    def __init__(self):
        self.heap = []   # [자료구조] 동적 배열(List) — 완전 이진 트리 형태로 사용

    # [알고리즘] 힙 삽입 (Heap Push)
    # - 새 후보를 배열 끝에 넣고 부모와 비교하며 위로 올림
    # - 시간 복잡도: O(log N)
    def push(self, item):
        self.heap.append(item)
        self._bubble_up(len(self.heap) - 1)

    # [알고리즘] 힙 삭제 (Heap Pop)
    # - 최솟값(root)을 꺼내고 마지막 원소를 root로 올린 뒤 아래로 내림
    # - 시간 복잡도: O(log N)
    def pop(self):
        if not self.heap:
            return None
        top = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self._sink_down(0)
        return top

    def is_empty(self):
        return len(self.heap) == 0

    # [알고리즘] 우선순위 계산
    # - priority 값이 있으면 우선 사용, 없으면 dist 값을 사용
    def _priority(self, item):
        return item.get("priority", item.get("dist", 0))

    # [알고리즘] 상향 재정렬 (Bubble Up)
    # - 자식 노드가 부모보다 비용이 작으면 교환
    def _bubble_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self._priority(self.heap[parent]) <= self._priority(self.heap[idx]):
                break
            self.heap[parent], self.heap[idx] = self.heap[idx], self.heap[parent]
            idx = parent

    # [알고리즘] 하향 재정렬 (Sink Down)
    # - root로 올라온 원소를 더 작은 자식과 교환하며 힙 속성 복구
    def _sink_down(self, idx):
        size = len(self.heap)
        while True:
            smallest = idx
            left = idx * 2 + 1
            right = idx * 2 + 2
            if left < size and self._priority(self.heap[left]) < self._priority(
                self.heap[smallest]
            ):
                smallest = left
            if right < size and self._priority(self.heap[right]) < self._priority(
                self.heap[smallest]
            ):
                smallest = right
            if smallest == idx:
                break
            self.heap[smallest], self.heap[idx] = self.heap[idx], self.heap[smallest]
            idx = smallest


# ==============================================================================
# 3. 알고리즘: 인접 간선 기반 최단 후보 탐색
# - 그래프에서 출발 노드(origin)에 연결된 간선을 순회
# - 각 간선의 도착 노드가 병원 후보가 됨
# - 검색 반경(radius) 이내 병원만 필터링하여 Top-K 선택 알고리즘으로 전달
# - 시간 복잡도: O(E + V) — E: 간선 수, V: 노드 수
#   (현재 구조에서는 origin -> 병원 간선 중심이므로 후보 병원 수에 비례)
# ==============================================================================

# [알고리즘] 인접 간선 후보 탐색
# - origin에서 연결된 병원 간선만 사용해 추천 후보 집합 생성
def find_nearest_hospitals_in_graph(hospital_graph, k, radius):
    origin_edges = hospital_graph.get_edges_from("origin")
    candidates = []
    for edge in origin_edges:
        node = hospital_graph.get_node(edge.get("to"))
        if node:
            candidates.append({**node, "edgeWeight": edge.get("weight")})

    filtered = [
        hospital
        for hospital in candidates
        if hospital.get("routeDistance") is not None
        and hospital.get("routeDistance") <= radius
    ]
    top_k_result = select_top_k_hospitals(filtered, k)

    return {
        "candidates": candidates,
        "filtered": filtered,
        "topK": top_k_result["topK"],
        "heapLog": top_k_result["heapLog"],   # 프론트엔드 힙 디버거 시각화용
        "radius": radius,
    }


# ==============================================================================
# 4. 알고리즘: Top-K 선택 (Top-K Selection)
# - 반경 필터를 통과한 병원 후보를 Min-Heap에 삽입
# - 이동 비용이 가장 낮은 병원부터 K개를 pop하여 추천 결과 생성
# - 정렬 전체를 수행하지 않고 필요한 K개만 선택
# - 시간 복잡도: O(N log N + K log N)
#   · N: 후보 병원 수
#   · K: 사용자가 선택한 최대 결과 개수
# ==============================================================================

# [알고리즘] Top-K 병원 선택
# - 거리 기준이면 dist=거리(m), 시간 기준이면 dist=소요시간(sec)
def select_top_k_hospitals(hospitals, k):
    priority_queue = MinHeap()
    heap_log = []

    # [알고리즘] 모든 후보 병원을 Min-Heap에 삽입
    for index, hospital in enumerate(hospitals):
        priority_queue.push(
            {"priority": hospital.get("dist", 0), "index": index, "hospital": hospital}
        )
        heap_log.append(
            {
                "action": "push",
                "hospital": hospital,
                "cost": hospital.get("dist", 0),
                "queueSnapshot": heap_snapshot(priority_queue),
            }
        )

    # [알고리즘] 비용이 낮은 순서대로 K개 추출
    top_k = []
    while not priority_queue.is_empty() and len(top_k) < k:
        item = priority_queue.pop()
        top_k.append(item["hospital"])
        heap_log.append(
            {
                "action": "pop",
                "hospital": item["hospital"],
                "cost": item.get("priority", 0),
                "queueSnapshot": heap_snapshot(priority_queue),
            }
        )

    return {"topK": top_k, "heapLog": heap_log}


# [자료구조] 힙 상태 스냅샷
# - 프론트엔드에서 Min-Heap 상태를 보여주기 위해 상위 5개 후보만 기록
def heap_snapshot(priority_queue):
    return [
        {"hospital": item["hospital"], "cost": item.get("priority", 0)}
        for item in priority_queue.heap[:5]
    ]


# ==============================================================================
# 5. 보조 알고리즘: Haversine 거리 계산
# - 위도/경도 두 점 사이의 구면 직선거리(m)를 계산
# - 직선거리 모드 또는 카카오 Directions API 실패 시 fallback 거리로 사용
# - 시간 복잡도: O(1)
# ==============================================================================

# [알고리즘] Haversine 거리 계산
def haversine(lat1, lng1, lat2, lng2):
    radius = 6371000
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return round(radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


# ==============================================================================
# Flask 라우팅: 추천 계산 API
# ==============================================================================

@bp_d.route("/api/memberD/recommend", methods=["POST"])
def recommend_hospitals_api():
    payload = request.get_json(silent=True) or {}
    origin = payload.get("origin") or {}
    hospitals = payload.get("hospitals") or []
    radius = int(payload.get("radius") or 2000)
    k = int(payload.get("k") or 3)
    metric = payload.get("metric") or "distance"

    origin_lat = to_float(origin.get("lat"))
    origin_lng = to_float(origin.get("lng"))
    if origin_lat is None or origin_lng is None:
        return jsonify({"error": "origin.lat and origin.lng are required"}), 400

    # [자료구조] 그래프 생성
    # - origin 노드를 먼저 추가한 뒤, 각 병원 후보를 hospital 노드로 추가
    hospital_graph = HospitalGraph()
    hospital_graph.add_node(
        {
            "id": "origin",
            "type": "origin",
            "name": "내 위치",
            "lat": origin_lat,
            "lng": origin_lng,
        }
    )

    # [알고리즘] 병원 후보 전처리 + 그래프 간선 구성
    # - 프론트엔드가 전달한 카카오 Places/Directions 결과를 그래프 노드와 간선으로 변환
    for hospital in hospitals:
        prepared = prepare_hospital_node(hospital, origin_lat, origin_lng, metric)
        if not prepared:
            continue
        hospital_graph.add_node({**prepared, "type": "hospital"})
        hospital_graph.add_edge(
            "origin",
            prepared["id"],
            prepared["dist"],
            {
                "routeDistance": prepared["routeDistance"],
                "routeDuration": prepared.get("routeDuration"),
                "routeSource": prepared.get("routeSource"),
            },
        )

    # [알고리즘] 인접 간선 후보 탐색 + Top-K 선택 호출
    return jsonify(find_nearest_hospitals_in_graph(hospital_graph, k, radius))


# [알고리즘] 병원 노드 전처리
# - 좌표/거리/시간 값을 숫자로 정규화
# - 도로 경로 데이터가 없으면 Haversine 직선거리로 보완
# - metric이 time이면 소요시간을 우선순위 비용으로 사용
def prepare_hospital_node(hospital, origin_lat, origin_lng, metric):
    hospital_id = str(hospital.get("id") or "").strip()
    lat = to_float(hospital.get("lat"))
    lng = to_float(hospital.get("lng"))
    if not hospital_id or lat is None or lng is None:
        return None

    fallback_distance = haversine(origin_lat, origin_lng, lat, lng)
    route_distance = to_float(hospital.get("routeDistance")) or fallback_distance
    route_duration = to_float(hospital.get("routeDuration"))
    if metric == "time" and route_duration is not None:
        dist = route_duration
    else:
        dist = to_float(hospital.get("dist")) or route_distance

    route_path = hospital.get("routePath") or [
        {"lat": origin_lat, "lng": origin_lng},
        {"lat": lat, "lng": lng},
    ]
    route_source = hospital.get("routeSource") or "straight"

    return {
        **hospital,
        "id": hospital_id,
        "lat": lat,
        "lng": lng,
        "dist": dist,
        "routeDistance": route_distance,
        "routeDuration": route_duration,
        "routePath": route_path,
        "routeSource": route_source,
    }


# [알고리즘] 숫자 변환 및 유효성 검사
# - 문자열/숫자 입력을 float로 변환
# - NaN/Infinity는 유효하지 않은 값으로 처리
def to_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


# ==============================================================================
# Flask 라우팅: 카카오모빌리티 길찾기 API 중계
# - 브라우저에서 REST API 키를 직접 노출하지 않기 위해 Python 서버가 대신 호출
# - 반환된 거리/시간/경로 좌표는 추천 API의 그래프 간선 가중치로 사용
# ==============================================================================

@bp_d.route("/api/directions")
def directions_api():
    rest_key = os.environ.get("KAKAO_REST_API_KEY")
    if not rest_key:
        return jsonify(
            {
                "error": "KAKAO_REST_API_KEY is not set",
                "message": "카카오모빌리티 길찾기 API를 쓰려면 REST API 키를 환경변수로 설정하세요.",
            }
        ), 503

    origin = request.args.get("origin")
    destination = request.args.get("destination")
    profile = request.args.get("profile") or "car"
    priority = request.args.get("priority") or "DISTANCE"

    if not origin or not destination:
        return jsonify({"error": "origin and destination are required"}), 400

    # [알고리즘] 라우팅 분기 — 이동 수단(profile)에 맞는 API URL 선택
    url = route_url(profile)
    if not url:
        return jsonify({"error": f"unsupported route profile: {profile}"}), 400

    # [자료구조] 해시 맵(Dictionary) — 카카오 Directions API 요청 파라미터
    # - origin/destination: "경도,위도" 형식
    # - priority: DISTANCE 또는 TIME
    request_params = {
        "origin": origin,
        "destination": destination,
        "priority": normalize_priority(profile, priority),
        "summary": "false",
    }
    if profile == "car":
        request_params["road_details"] = "true"

    kakao_query = urlencode(request_params)
    kakao_request = Request(
        f"{url}?{kakao_query}",
        headers={
            "Authorization": f"KakaoAK {rest_key}",
            "service": "petcare",
            "Content-Type": "application/json",
        },
    )

    # [알고리즘] 외부 API 호출 — 카카오모빌리티 도로 경로 계산 결과 수신
    try:
        with urlopen(kakao_request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        return jsonify({"error": "kakao api error", "detail": body}), err.code
    except (URLError, TimeoutError) as err:
        return jsonify({"error": "directions request failed", "detail": str(err)}), 502

    routes = payload.get("routes") or []
    if not routes:
        return jsonify({"error": "empty directions response"}), 502

    route = routes[0]
    if route.get("result_code") != 0:
        return jsonify(
            {
                "error": "directions failed",
                "code": route.get("result_code"),
                "message": route.get("result_msg"),
            }
        ), 502

    summary = route.get("summary") or {}
    path = []   # [자료구조] 동적 배열(List) — 지도 폴리라인 좌표 목록

    # [알고리즘] 경로 좌표 파싱 (Linear Scan)
    # - sections -> roads -> vertexes 배열을 순차 탐색
    # - vertexes는 [lng0, lat0, lng1, lat1, ...] 구조이므로 2칸씩 읽음
    # - 시간 복잡도: O(P) — P: 전체 좌표 값 개수
    for section in route.get("sections") or []:
        for road in section.get("roads") or []:
            vertexes = road.get("vertexes") or []
            for i in range(0, len(vertexes) - 1, 2):
                path.append({"lng": vertexes[i], "lat": vertexes[i + 1]})

    return jsonify(
        {
            "distance": summary.get("distance"),
            "duration": summary.get("duration"),
            "path": path,
            "source": f"kakao-directions-{profile}",
        }
    )


# [알고리즘] 라우팅 분기 함수
# - 현재 프로젝트에서는 차량(car) 경로만 지원
# - 도보/자전거 API가 추가되면 이 매핑에 엔드포인트를 확장
def route_url(profile):
    if profile == "car":
        return KAKAO_DIRECTIONS_URL
    return None


# [알고리즘] 우선순위 정규화
# - 카카오 API가 허용하지 않는 priority가 들어오면 DISTANCE로 보정
def normalize_priority(profile, priority):
    if profile == "car" and priority not in ("RECOMMEND", "TIME", "DISTANCE"):
        return "DISTANCE"
    return priority


# ==============================================================================
# 독립 실행 모드용 HTTP 핸들러
# - Flask app.py를 거치지 않고 memberD.py만 직접 실행할 때 사용
# - Flask 라우트와 동일하게 /api/memberD/recommend, /api/directions를 처리
# ==============================================================================

class PetCareHandler(SimpleHTTPRequestHandler):
    # [알고리즘] GET 요청 경로 분기
    # - /api/directions만 직접 처리하고 나머지는 정적 파일 서버로 위임
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/directions":
            self.handle_directions(parsed.query)
            return
        super().do_GET()

    # [알고리즘] POST 요청 경로 분기
    # - /api/memberD/recommend 요청을 Python 추천 엔진으로 연결
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/memberD/recommend":
            self.handle_recommend()
            return
        self.send_json(404, {"error": "not found"})

    def handle_recommend(self):
        content_length = int(self.headers.get("Content-Length") or 0)
        try:
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json(400, {"error": "invalid json body"})
            return

        origin = payload.get("origin") or {}
        hospitals = payload.get("hospitals") or []
        radius = int(payload.get("radius") or 2000)
        k = int(payload.get("k") or 3)
        metric = payload.get("metric") or "distance"

        origin_lat = to_float(origin.get("lat"))
        origin_lng = to_float(origin.get("lng"))
        if origin_lat is None or origin_lng is None:
            self.send_json(400, {"error": "origin.lat and origin.lng are required"})
            return

        # [자료구조] 그래프 생성 — Flask 추천 API와 동일한 로직
        hospital_graph = HospitalGraph()
        hospital_graph.add_node(
            {
                "id": "origin",
                "type": "origin",
                "name": "내 위치",
                "lat": origin_lat,
                "lng": origin_lng,
            }
        )

        # [알고리즘] 병원 후보 전처리 + 그래프 간선 구성
        for hospital in hospitals:
            prepared = prepare_hospital_node(hospital, origin_lat, origin_lng, metric)
            if not prepared:
                continue
            hospital_graph.add_node({**prepared, "type": "hospital"})
            hospital_graph.add_edge(
                "origin",
                prepared["id"],
                prepared["dist"],
                {
                    "routeDistance": prepared["routeDistance"],
                    "routeDuration": prepared.get("routeDuration"),
                    "routeSource": prepared.get("routeSource"),
                },
            )

        self.send_json(200, find_nearest_hospitals_in_graph(hospital_graph, k, radius))

    def handle_directions(self, query):
        rest_key = os.environ.get("KAKAO_REST_API_KEY")
        if not rest_key:
            self.send_json(
                503,
                {
                    "error": "KAKAO_REST_API_KEY is not set",
                    "message": "카카오모빌리티 길찾기 API를 쓰려면 REST API 키를 환경변수로 설정하세요.",
                },
            )
            return

        # [자료구조] 해시 맵(Dictionary) — URL 쿼리 파라미터 파싱 결과
        params = parse_qs(query)
        origin = self.first(params, "origin")
        destination = self.first(params, "destination")
        profile = self.first(params, "profile") or "car"
        priority = self.first(params, "priority") or "DISTANCE"

        if not origin or not destination:
            self.send_json(400, {"error": "origin and destination are required"})
            return

        url = self.route_url(profile)
        if not url:
            self.send_json(400, {"error": f"unsupported route profile: {profile}"})
            return

        # [자료구조] 해시 맵(Dictionary) — 카카오 Directions API 요청 파라미터
        request_params = {
            "origin": origin,
            "destination": destination,
            "priority": self.normalize_priority(profile, priority),
            "summary": "false",
        }
        if profile == "car":
            request_params["road_details"] = "true"

        kakao_query = urlencode(
            request_params
        )
        request = Request(
            f"{url}?{kakao_query}",
            headers={
                "Authorization": f"KakaoAK {rest_key}",
                "service": "petcare",
                "Content-Type": "application/json",
            },
        )

        # [알고리즘] 외부 API 호출 — 카카오 도로 경로 계산 결과 수신
        try:
            with urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            body = err.read().decode("utf-8", errors="replace")
            self.send_json(err.code, {"error": "kakao api error", "detail": body})
            return
        except (URLError, TimeoutError) as err:
            self.send_json(502, {"error": "directions request failed", "detail": str(err)})
            return

        routes = payload.get("routes") or []
        if not routes:
            self.send_json(502, {"error": "empty directions response"})
            return

        route = routes[0]
        if route.get("result_code") != 0:
            self.send_json(
                502,
                {
                    "error": "directions failed",
                    "code": route.get("result_code"),
                    "message": route.get("result_msg"),
                },
            )
            return

        summary = route.get("summary") or {}
        path = []   # [자료구조] 동적 배열(List) — 지도 폴리라인 좌표 목록

        # [알고리즘] 경로 좌표 파싱 (Linear Scan)
        for section in route.get("sections") or []:
            for road in section.get("roads") or []:
                vertexes = road.get("vertexes") or []
                for i in range(0, len(vertexes) - 1, 2):
                    path.append({"lng": vertexes[i], "lat": vertexes[i + 1]})

        self.send_json(
            200,
            {
                "distance": summary.get("distance"),
                "duration": summary.get("duration"),
                "path": path,
                "source": f"kakao-directions-{profile}",
            },
        )

    # [알고리즘] JSON 응답 직렬화
    # - Python dict/list 자료구조를 JSON 문자열로 변환하여 브라우저에 전달
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # [알고리즘] 쿼리 파라미터 단일 값 추출
    @staticmethod
    def first(params, key):
        values = params.get(key)
        return values[0] if values else None

    @staticmethod
    def route_url(profile):
        return route_url(profile)

    @staticmethod
    def normalize_priority(profile, priority):
        return normalize_priority(profile, priority)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    server = ThreadingHTTPServer(("127.0.0.1", port), PetCareHandler)
    print(f"Serving Pet Care Guide at http://localhost:{port}/memberD.html")
    server.serve_forever()
