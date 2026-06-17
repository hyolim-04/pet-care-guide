from flask import Blueprint, request, jsonify, send_from_directory
from datetime import date

bp_a = Blueprint('module_a', __name__)

# ════════════════════════════════════════════════════════════
#  공유 데이터 (memberB에서 import해서 씀)
# ════════════════════════════════════════════════════════════

# [자료구조] 동적 배열 (Dynamic Array / Python List)
# - dogs: 등록된 강아지 객체를 순서대로 저장하는 리스트
# - 삽입(append): O(1) 평균 / 순차 탐색: O(n)
dogs = []

# [자료구조] 해시 맵 (Hash Map / Python Dictionary)
# - logs: dog_id(정수)를 키로, 해당 강아지의 건강 로그 배열을 값으로 저장
# - 키 기반 조회: O(1) 평균
logs = {}

BREEDS = ["말티즈", "포메라니안", "푸들 (토이/미니어처)", "시츄", "골든 리트리버", "비숑 프리제", "진돗개", "웰시 코기"]
CHRONIC_DISEASES = ["없음", "비만", "당뇨", "심장병", "신장병 (콩팥병)", "관절염", "쿠싱증후군", "갑상선 기능 저하증", "간질환", "피부 알레르기", "식품 알레르기", "안과 질환 (백내장 등)", "치주 질환"]
SYMPTOMS = ["없음", "식욕 감소", "구토", "설사", "기침 / 재채기", "무기력 / 활동량 감소", "과도한 음수 (물 많이 마심)", "긁음 / 피부 발진", "절뚝거림", "눈곱 / 눈물 과다", "배변 이상 (변비 등)", "체중 급변"]

# ════════════════════════════════════════════════════════════
#  모듈 A 알고리즘
# ════════════════════════════════════════════════════════════

# [알고리즘] 규칙 기반 분류 (Rule-Based Classification)
# - 나이·체중 변화량·활동량 조건을 순서대로 비교해 건강 유형을 결정
# - 시간 복잡도: O(1) — 조건 분기 수가 고정
def classify_type(dog, log, prev_log):
    if dog["age"] >= 8: return {"key": "senior", "label": "🧓 노령견 관리"}
    weight_trend = (log["weight"] - prev_log["weight"]) if prev_log else 0
    if weight_trend > 0.3: return {"key": "diet", "label": "⚠️ 체중 감량 필요"}
    if weight_trend < -0.3: return {"key": "gain", "label": "📈 체중 증가 필요"}
    if log["activity"] == "높음": return {"key": "maintain", "label": "✅ 정상 유지 (활동형)"}
    return {"key": "maintain", "label": "✅ 정상 유지"}

# [알고리즘] 선택 정렬 (Selection Sort)
# - 매 반복마다 미정렬 구간에서 최솟값을 찾아 맨 앞 원소와 교환
# - 시간 복잡도: O(n²) / 공간 복잡도: O(1) (in-place)
# - 교환 횟수가 적어 소규모 로그 데이터 정렬에 적합
# - steps 리스트에 각 교환 과정을 기록하여 시각적 피드백 제공
def selection_sort_logs(arr, key):
    arr = [dict(l) for l in arr]
    n = len(arr)
    steps = []
    for i in range(n - 1):
        min_idx = i                          # 현재 구간의 최솟값 인덱스 초기화
        for j in range(i + 1, n):
            if arr[j][key] < arr[min_idx][key]: min_idx = j   # 최솟값 갱신
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]        # 교환
            steps.append(f"i={i}: [{i}]↔[{min_idx}] 교환 ({arr[i][key]} ↔ {arr[min_idx][key]})")
    return arr, steps

# [알고리즘] 이진 탐색 (Binary Search)
# - 날짜 기준으로 오름차순 정렬된 로그 배열에서 특정 날짜 검색
# - 전제 조건: 입력 배열이 date 키 기준으로 정렬되어 있어야 함
# - 시간 복잡도: O(log n) — 매 단계마다 탐색 범위를 절반으로 축소
# - steps 리스트에 각 단계의 lo/hi/mid 값을 기록하여 탐색 과정 시각화
def binary_search_logs(arr, target):
    lo, hi, step = 0, len(arr) - 1, 1
    steps = []
    while lo <= hi:
        mid = (lo + hi) // 2                # 중간 인덱스 계산
        steps.append(f"Step {step}: lo={lo}, hi={hi}, mid={mid} → \"{arr[mid]['date']}\"")
        step += 1
        if arr[mid]["date"] == target:
            steps.append(f"✔ 일치! index = {mid}")
            return mid, steps
        elif arr[mid]["date"] < target: lo = mid + 1   # 오른쪽 절반 탐색
        else: hi = mid - 1                             # 왼쪽 절반 탐색
    return -1, steps

# ════════════════════════════════════════════════════════════
#  모듈 A API 라우트
# ════════════════════════════════════════════════════════════
@bp_a.route("/memberA")
def member_a_page(): return send_from_directory("static", "memberA.html")

@bp_a.route("/api/options", methods=["GET"])
def get_options(): return jsonify({"breeds": BREEDS, "diseases": CHRONIC_DISEASES, "symptoms": SYMPTOMS})

@bp_a.route("/api/dogs", methods=["GET"])
def get_dogs(): return jsonify(dogs)

@bp_a.route("/api/dogs", methods=["POST"])
def register_dog():
    data = request.get_json()
    diseases = data.get("diseases", ["없음"])
    if not isinstance(diseases, list) or len(diseases) == 0:
        diseases = ["없음"]
    # [자료구조] 딕셔너리(Dictionary)로 강아지 객체 생성 후 동적 배열(dogs)에 추가
    dog = {
        "id": len(dogs) + 1, "name": data.get("name", "").strip(), "breed": data.get("breed", "").strip(),
        "age": int(data.get("age", 0)), "weight": float(data.get("weight", 0)),
        "size": data.get("size", "small"), "diseases": diseases,
    }
    dogs.append(dog)
    logs[dog["id"]] = []   # 해시 맵에 해당 강아지의 빈 로그 배열 초기화
    return jsonify({"ok": True, "dog": dog})

@bp_a.route("/api/dogs/<int:dog_id>/logs", methods=["GET"])
def get_logs(dog_id): return jsonify(logs.get(dog_id, []))

@bp_a.route("/api/dogs/<int:dog_id>/logs", methods=["POST"])
def add_log(dog_id):
    dog = next((d for d in dogs if d["id"] == dog_id), None)
    data = request.get_json()
    new_weight = float(data.get("weight", 0))
    arr = logs[dog_id]
    prev = arr[-1] if arr else None
    # [알고리즘] 규칙 기반 분류 호출 — 직전 로그와 현재 로그를 비교해 건강 유형 판정
    health_type = classify_type(dog, {"weight": new_weight, "activity": data.get("activity", "보통")}, prev)
    new_log = {"date": data.get("date") or str(date.today()), "weight": new_weight,
               "activity": data.get("activity", "보통"), "memo": data.get("memo", ""), "type": health_type}
    arr.append(new_log)
    dog["weight"] = new_weight
    return jsonify({"ok": True, "log": new_log})

@bp_a.route("/api/dogs/<int:dog_id>/logs/<int:log_idx>", methods=["DELETE"])
def delete_log(dog_id, log_idx):
    if dog_id not in logs or log_idx >= len(logs[dog_id]):
        return jsonify({"error": "존재하지 않는 기록입니다."}), 404
    removed = logs[dog_id].pop(log_idx)   # [자료구조] 동적 배열 인덱스 삭제: O(n)
    return jsonify({"ok": True, "removed": removed})

@bp_a.route("/api/dogs/<int:dog_id>/diseases", methods=["PUT"])
def update_diseases(dog_id):
    dog = next((d for d in dogs if d["id"] == dog_id), None)
    if not dog: return jsonify({"error": "존재하지 않는 강아지입니다."}), 404
    data = request.get_json()
    diseases = data.get("diseases", ["없음"])
    if not isinstance(diseases, list) or len(diseases) == 0:
        diseases = ["없음"]
    dog["diseases"] = diseases
    return jsonify({"ok": True, "diseases": diseases})

@bp_a.route("/api/dogs/<int:dog_id>/sort", methods=["GET"])
def sort_logs(dog_id):
    if dog_id not in logs: return jsonify({"error": "존재하지 않는 강아지입니다."}), 404
    key = request.args.get("key", "date")
    # [알고리즘] 선택 정렬 호출 — date 또는 weight 키 기준으로 로그 정렬
    sorted_arr, steps = selection_sort_logs(logs[dog_id], key)
    logs[dog_id] = sorted_arr
    return jsonify({"ok": True, "logs": sorted_arr, "steps": steps, "sorted_by": key})

@bp_a.route("/api/dogs/<int:dog_id>/search", methods=["GET"])
def search_log(dog_id):
    if dog_id not in logs: return jsonify({"error": "존재하지 않는 강아지입니다."}), 404
    target = request.args.get("date", "")
    # [알고리즘] 이진 탐색 전처리 — 탐색 전 반드시 date 기준 오름차순 정렬 수행
    arr = sorted(logs[dog_id], key=lambda x: x["date"])
    logs[dog_id] = arr
    # [알고리즘] 이진 탐색 호출 — 정렬된 배열에서 특정 날짜 로그 검색
    found_idx, steps = binary_search_logs(arr, target)
    if found_idx == -1: return jsonify({"ok": False, "steps": steps, "message": f'"{target}" 날짜의 기록이 없습니다.'})
    return jsonify({"ok": True, "steps": steps, "log": arr[found_idx], "index": found_idx})
