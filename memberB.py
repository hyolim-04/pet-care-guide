from flask import Blueprint, jsonify, send_from_directory
import memberA



# [자료구조] 모듈 간 공유 참조 (Shared Reference)
# - memberA의 dogs/logs 객체를 직접 참조(reference)하여 동일한 메모리 공간 공유
# - 복사가 아닌 참조이므로 memberA에서 데이터 변경 시 memberB에도 즉시 반영됨
dogs = memberA.dogs
logs = memberA.logs
bp_b = Blueprint('module_b', __name__)

# ════════════════════════════════════════════════════════════
#  질병 분류 (A·B·C 공통)
#  CHRONIC_DISEASES = ["없음", "심장병", "신장병", "관절염", "알레르기", "호르몬질환", "종양"]
#  - "없음"은 추천 시 conditions에서 제외되므로 매핑 불필요
#  - 사료 특화 플래그(6종): has_heart_supp / has_kidney_supp / has_joint_supp
#                          has_allergy_supp / has_hormone_supp / has_tumor_supp
# ════════════════════════════════════════════════════════════

# [자료구조] 중첩 딕셔너리 + 리스트 (Nested Dictionary + List)
# - 사이즈("small"/"medium"/"large")를 키로, 사료 객체 리스트를 값으로 저장
# - 버킷(bucket) 구조: 강아지 크기별로 사료 후보군을 분리해 탐색 범위를 O(전체→버킷크기)로 축소
# - 각 버킷마다 6개 질환(심장/신장/관절/알레르기/호르몬/종양)을 모두 커버하도록 구성하여
#   어떤 기저질환 조합이 들어와도 매칭 사료가 다양하게 추천되도록 함
FOOD_DATABASE = {
    "small": [
        {"id": 1,  "name": "소형견 심장 케어 처방식", "price": 38000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": True,  "has_kidney_supp": False, "is_diet": True},
        {"id": 2,  "name": "소형견 신장 처방식", "price": 40000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True,  "is_diet": False},
        {"id": 3,  "name": "소형견 관절 튼튼 스몰바이트", "price": 25000, "age_target": "adult",  "protein": "normal", "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 4,  "name": "소형견 저알러지 가수분해 케어", "price": 34000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True},
        {"id": 5,  "name": "소형견 호르몬(당뇨/갑상선/쿠싱) 대사 케어", "price": 39000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_hormone_supp": True},
        {"id": 6,  "name": "소형견 항산화 종양 케어", "price": 41000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_tumor_supp": True},
        {"id": 7,  "name": "소형견 심장/신장 올인원 케어", "price": 42000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": True,  "has_kidney_supp": True,  "is_diet": False},
        {"id": 8,  "name": "소형견 관절/종양 시니어 케어", "price": 37000, "age_target": "senior", "protein": "low",    "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_tumor_supp": True},
        {"id": 9,  "name": "소형견 알러지/호르몬 통합 케어", "price": 36000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_allergy_supp": True, "has_hormone_supp": True},
        {"id": 10, "name": "퍼피 고단백 스몰", "price": 28000, "age_target": "puppy",  "protein": "high",   "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 11, "name": "퍼피 소화/관절 튼튼", "price": 31000, "age_target": "puppy",  "protein": "high",   "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 12, "name": "소형견 체중 관리 다이어트", "price": 22000, "age_target": "adult",  "protein": "low",    "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 13, "name": "소형견 데일리 유지용", "price": 19000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
    ],
    "medium": [
        {"id": 20, "name": "중형견 심장/신장 집중 케어", "price": 55000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": True,  "has_kidney_supp": True,  "is_diet": False},
        {"id": 21, "name": "중형견 신장 저단백 처방식", "price": 52000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True,  "is_diet": False},
        {"id": 22, "name": "중형견 체중 감량/관절 케어", "price": 51000, "age_target": "adult",  "protein": "low",    "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 23, "name": "중형견 저알러지 가수분해 케어", "price": 53000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True},
        {"id": 24, "name": "중형견 호르몬(당뇨/갑상선/쿠싱) 대사 케어", "price": 52000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_hormone_supp": True},
        {"id": 25, "name": "중형견 항산화 종양 케어", "price": 54000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_tumor_supp": True},
        {"id": 26, "name": "중형견 심장 케어 시니어", "price": 50000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": True,  "has_kidney_supp": False, "is_diet": True},
        {"id": 27, "name": "중형견 관절/종양 시니어 케어", "price": 56000, "age_target": "senior", "protein": "normal", "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_tumor_supp": True},
        {"id": 28, "name": "중형견 알러지/호르몬 통합 케어", "price": 53000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_allergy_supp": True, "has_hormone_supp": True},
        {"id": 29, "name": "중형견 고단백 액티브", "price": 47000, "age_target": "adult",  "protein": "high",   "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 30, "name": "미디엄 퍼피 성장 조절", "price": 46000, "age_target": "puppy",  "protein": "high",   "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 31, "name": "미디엄 어덜트 유지용", "price": 45000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
    ],
    "large": [
        {"id": 40, "name": "대형견 심장/관절 시니어", "price": 72000, "age_target": "senior", "protein": "normal", "has_joint_supp": True,  "has_heart_supp": True,  "has_kidney_supp": False, "is_diet": False},
        {"id": 41, "name": "대형견 신장 처방식", "price": 75000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True,  "is_diet": False},
        {"id": 42, "name": "대형견 관절 특화 성견용", "price": 65000, "age_target": "adult",  "protein": "normal", "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 43, "name": "대형견 저알러지 가수분해 케어", "price": 71000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True},
        {"id": 44, "name": "대형견 호르몬(당뇨/갑상선/쿠싱) 대사 케어", "price": 70000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_hormone_supp": True},
        {"id": 45, "name": "대형견 항산화 종양 케어", "price": 73000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_tumor_supp": True},
        {"id": 46, "name": "대형견 심장/신장 올인원 케어", "price": 76000, "age_target": "senior", "protein": "low",    "has_joint_supp": False, "has_heart_supp": True,  "has_kidney_supp": True,  "is_diet": False},
        {"id": 47, "name": "대형견 관절/종양 시니어 케어", "price": 74000, "age_target": "senior", "protein": "low",    "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_tumor_supp": True},
        {"id": 48, "name": "대형견 알러지/호르몬 통합 케어", "price": 72000, "age_target": "adult",  "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True,  "has_allergy_supp": True, "has_hormone_supp": True},
        {"id": 49, "name": "대형견 고단백 머슬 핏", "price": 68000, "age_target": "adult",  "protein": "high",   "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 50, "name": "라지 퍼피 튼튼 골격", "price": 62000, "age_target": "puppy",  "protein": "high",   "has_joint_supp": True,  "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 51, "name": "라지 라이트 다이어트", "price": 58000, "age_target": "adult",  "protein": "low",    "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
    ]
}

# [자료구조] 질환→사료 매핑 테이블 (Disease-to-Food Mapping Table)
# - 기저질환 문자열을 키로, (사료 플래그, 추천 사유) 튜플을 값으로 저장하는 해시 맵
# - WSM에서 if 분기를 늘리는 대신 이 표만 확장하면 신규 질환 대응 가능 (확장성/유지보수성 ↑)
# - 키는 CHRONIC_DISEASES와 1:1로 맞춤 ("없음"은 conditions에서 사전 제외되므로 제외)
DISEASE_FOOD_MAP = {
    "심장병":   ("has_heart_supp",   "심장병 특화 사료"),
    "신장병":   ("has_kidney_supp",  "신장병 특화 사료"),
    "관절염":   ("has_joint_supp",   "관절염 특화 사료"),
    "알레르기": ("has_allergy_supp", "알레르기(저알러지) 케어 사료"),
    "호르몬질환": ("has_hormone_supp", "호르몬질환(당뇨/갑상선/쿠싱) 대사 케어 사료"),
    "종양":     ("has_tumor_supp",   "종양(항산화/면역) 케어 사료"),
}

def check_obesity(size, weight):
    if size == "small" and weight > 8.0: return True
    if size == "medium" and weight > 20.0: return True
    if size == "large" and weight > 35.0: return True
    return False

def check_underweight(size, weight):
    if size == "small" and weight < 2.0: return True
    if size == "medium" and weight < 8.0: return True
    if size == "large" and weight < 20.0: return True
    return False

# [알고리즘] 가중치 합산 모델 (Weighted Sum Model, WSM)
# - 다기준 의사결정(MCDM) 기법: 각 평가 기준에 가중 점수를 부여하고 합산해 최적 대안 선택
# - 평가 기준 및 가중치:
#     · 기저질환 특화 사료 매칭 (심장/신장/관절/알레르기/호르몬/종양): +80점 (최우선, 보유 질환별 누적)
#     · 연령 그룹 일치 (puppy/adult/senior):                          +40점
#     · 체형(비만/저체중/정상) 적합성:                                 +15~25점
#     · 견종 크기별 키블 적합성:                                       +10점 (기본)
# - 시간 복잡도: O(k) — k는 평가 기준 수(고정값이므로 사실상 O(1))
def calculate_wsm(profile, food):
    score = 0
    reasons = []
    conditions = profile.get("conditions", [])

    # [자료구조/알고리즘] 매핑 테이블 기반 질환 매칭 — 보유 질환마다 사료 플래그를 O(1) 조회
    # - matched_flags: 동일 플래그 중복 가점 방지 (보유 질환이 같은 사료 특화에 동시 매칭될 때)
    # - 질환을 여러 개 보유하면 매칭되는 만큼 +80점이 누적되어 다질환 케어 사료가 상위로 올라옴
    matched_flags = set()
    for cond in conditions:
        entry = DISEASE_FOOD_MAP.get(cond)
        if not entry:
            continue
        flag, label = entry
        if flag not in matched_flags and food.get(flag):
            score += 80
            reasons.append({"점수": 80, "사유": label})
            matched_flags.add(flag)

    if profile["age_group"] == food["age_target"]:
        score += 40
        label = {"puppy": "퍼피 발달 맞춤 영양", "senior": "시니어 노화 방지/저단백"}.get(profile["age_group"], "성견 유지용 적합")
        reasons.append({"점수": 40, "사유": label})

    if profile.get("is_obese") and food["is_diet"]:
        score += 25; reasons.append({"점수": 25, "사유": "비만 판정: 다이어트/저지방 특화"})
    elif profile.get("is_underweight") and food.get("protein") == "high" and not food["is_diet"]:
        score += 25; reasons.append({"점수": 25, "사유": "저체중 판정: 고단백 영양 공급 특화"})
    elif not profile.get("is_obese") and not profile.get("is_underweight") and not food["is_diet"]:
        score += 15; reasons.append({"점수": 15, "사유": "일반 체형 유지용"})

    score += 10
    size_kr = {"small": "소형", "medium": "중형", "large": "대형"}.get(profile["size"], "소형")
    reasons.append({"점수": 10, "사유": f"{size_kr}견 전용 알갱이(키블) 크기"})

    return score, reasons

# [알고리즘] 병합 정렬 (Merge Sort) — 분할 정복(Divide & Conquer) 패턴
# - WSM 점수 내림차순으로 사료 리스트를 정렬하여 상위 추천 목록 도출
# - 동점 시 가격 오름차순으로 정렬 (더 저렴한 사료 우선)
# - 시간 복잡도: O(n log n) / 공간 복잡도: O(n) — 안정 정렬(stable sort)
# - 선택 정렬(memberA) 대비 대용량 데이터에서 성능 우위
def merge_sort(arr):
    if len(arr) <= 1: return arr          # 기저 조건(base case): 원소 1개 이하
    mid = len(arr) // 2
    # 분할(Divide): 절반으로 재귀 분할
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

# [알고리즘] 병합 정렬 — 병합(Merge) 단계
# - 두 정렬된 부분 배열을 점수 내림차순(동점 시 가격 오름차순)으로 병합
def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]["score"] > right[j]["score"]:
            result.append(left[i]); i += 1
        elif left[i]["score"] < right[j]["score"]:
            result.append(right[j]); j += 1
        else:
            # 동점 처리: 가격이 낮은 사료 우선
            if left[i]["price"] <= right[j]["price"]: result.append(left[i]); i += 1
            else: result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

@bp_b.route("/memberB")
def member_b_page():
    return send_from_directory("static", "memberB.html")

@bp_b.route("/api/recommend/<int:dog_id>", methods=["GET"])
def recommend_api(dog_id):
    dog = next((d for d in dogs if d["id"] == dog_id), None)
    if not dog: return jsonify({"error": "등록된 강아지 정보가 없습니다."}), 404

    dog_logs = logs.get(dog_id, [])
    latest_weight = dog["weight"]
    latest_activity = "보통"
    if dog_logs:
        # [알고리즘] Python 내장 정렬(Timsort) — 최신 로그 추출을 위한 날짜 오름차순 정렬
        # Timsort: O(n log n) 최악 / O(n) 최선(부분 정렬된 데이터에 최적화)
        sorted_logs = sorted(dog_logs, key=lambda x: x["date"])
        latest_weight = sorted_logs[-1]["weight"]
        latest_activity = sorted_logs[-1]["activity"]

    mapped_activity = {"낮음": "low", "보통": "medium", "높음": "high"}.get(latest_activity, "medium")
    conditions = [c for c in dog["diseases"] if c != "없음"]
    age = dog["age"]
    age_group = "puppy" if age < 1 else "senior" if age >= 8 else "adult"
    size = dog.get("size") or ("small" if latest_weight <= 8 else "medium" if latest_weight <= 20 else "large")

    # [자료구조] 딕셔너리(Dictionary) — 강아지 프로파일 객체 구성
    profile = {
        "name": dog["name"], "breed": dog["breed"], "age": age, "weight": latest_weight,
        "size": size, "activity": mapped_activity, "conditions": conditions,
        "age_group": age_group,
        "is_obese": check_obesity(size, latest_weight),
        "is_underweight": check_underweight(size, latest_weight)
    }

    # [자료구조] 버킷 기반 해시 맵 조회 — 크기별 사료 버킷에서 후보군 추출: O(1)
    target_bucket = FOOD_DATABASE.get(size, [])

    # [알고리즘] WSM 점수 계산 후 병합 정렬로 상위 3개 추천 사료 선정
    processed_foods = []
    for food in target_bucket:
        score, reasons = calculate_wsm(profile, food)
        f = food.copy(); f["score"] = score; f["reasons"] = reasons
        processed_foods.append(f)

    return jsonify({
        "profile": profile,
        "total_count": sum(len(v) for v in FOOD_DATABASE.values()),
        "bucket_count": len(target_bucket),
        # [알고리즘] 병합 정렬 호출 — 점수 내림차순 정렬 후 상위 3개 슬라이싱
        "top3": merge_sort(processed_foods)[:3]
    })