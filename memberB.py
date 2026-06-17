from flask import Blueprint, jsonify, send_from_directory
import memberA



# [자료구조] 모듈 간 공유 참조 (Shared Reference)
# - memberA의 dogs/logs 객체를 직접 참조(reference)하여 동일한 메모리 공간 공유
# - 복사가 아닌 참조이므로 memberA에서 데이터 변경 시 memberB에도 즉시 반영됨
dogs = memberA.dogs
logs = memberA.logs
bp_b = Blueprint('module_b', __name__)

# [자료구조] 중첩 딕셔너리 + 리스트 (Nested Dictionary + List)
# - 사이즈("small"/"medium"/"large")를 키로, 사료 객체 리스트를 값으로 저장
# - 버킷(bucket) 구조: 강아지 크기별로 사료 후보군을 분리해 탐색 범위를 O(전체→버킷크기)로 축소
FOOD_DATABASE = {
    "small": [
        {"id": 1, "name": "시니어 관절 케어", "price": 32000, "age_target": "senior", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 2, "name": "관절 튼튼 스몰바이트", "price": 25000, "age_target": "adult", "protein": "normal", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 3, "name": "심장 케어 소형견용", "price": 38000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": True},
        {"id": 4, "name": "퍼피 고단백 스몰", "price": 28000, "age_target": "puppy", "protein": "high", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 5, "name": "소형견 체중 관리", "price": 22000, "age_target": "adult", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 6, "name": "올인원 신장/심장 케어 스몰", "price": 42000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": True, "is_diet": False},
        {"id": 7, "name": "소형견 고단백 영양 부스터", "price": 27000, "age_target": "adult", "protein": "high", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 8, "name": "퍼피 소화/관절 튼튼", "price": 31000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 9, "name": "소형견 데일리 유지용", "price": 19000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 22, "name": "소형견 당뇨/갑상선 대사 케어", "price": 36000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_diabetes_supp": True, "has_thyroid_supp": True},
        {"id": 23, "name": "소형견 간/쿠싱 저지방 처방식", "price": 39000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_liver_supp": True, "has_cushing_supp": True},
        {"id": 24, "name": "소형견 저알러지 가수분해 케어", "price": 34000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_skin_supp": True, "has_food_allergy_supp": True},
        {"id": 25, "name": "소형견 시니어 안과/치주 케어", "price": 33000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_eye_supp": True, "has_dental_supp": True},
    ],
    "medium": [
        {"id": 10, "name": "미디엄 어덜트 유지용", "price": 45000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 11, "name": "미디엄 시니어 다이어트", "price": 48000, "age_target": "senior", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 12, "name": "미디엄 퍼피 성장 조절", "price": 46000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 13, "name": "미디엄 심장/신장 집중 케어", "price": 55000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": True, "is_diet": False},
        {"id": 14, "name": "중형견 고단백 액티브", "price": 47000, "age_target": "adult", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 15, "name": "중형견 체중 감량/관절", "price": 51000, "age_target": "adult", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 26, "name": "중형견 당뇨/갑상선 대사 케어", "price": 52000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_diabetes_supp": True, "has_thyroid_supp": True},
        {"id": 27, "name": "중형견 간/쿠싱 저지방 처방식", "price": 56000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_liver_supp": True, "has_cushing_supp": True},
        {"id": 28, "name": "중형견 저알러지 가수분해 케어", "price": 53000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_skin_supp": True, "has_food_allergy_supp": True},
        {"id": 29, "name": "중형견 시니어 안과/치주 케어", "price": 50000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_eye_supp": True, "has_dental_supp": True},
    ],
    "large": [
        {"id": 16, "name": "라지 관절 특화 성견용", "price": 65000, "age_target": "adult", "protein": "normal", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 17, "name": "라지 퍼피 튼튼 골격", "price": 62000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 18, "name": "대형견 심장/관절 시니어", "price": 72000, "age_target": "senior", "protein": "normal", "has_joint_supp": True, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": False},
        {"id": 19, "name": "라지 라이트 다이어트", "price": 58000, "age_target": "adult", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True},
        {"id": 20, "name": "대형견 고단백 머슬 핏", "price": 68000, "age_target": "adult", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False},
        {"id": 21, "name": "대형견 신장 처방식", "price": 75000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False},
        {"id": 30, "name": "대형견 당뇨/갑상선 대사 케어", "price": 70000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_diabetes_supp": True, "has_thyroid_supp": True},
        {"id": 31, "name": "대형견 간/쿠싱 저지방 처방식", "price": 74000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_liver_supp": True, "has_cushing_supp": True},
        {"id": 32, "name": "대형견 저알러지 가수분해 케어", "price": 71000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_skin_supp": True, "has_food_allergy_supp": True},
        {"id": 33, "name": "대형견 시니어 안과/치주 케어", "price": 69000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_eye_supp": True, "has_dental_supp": True},
    ]
}

# [자료구조] 질환→사료 매핑 테이블 (Disease-to-Food Mapping Table)
# - 기저질환 문자열을 키로, (사료 플래그, 추천 사유) 튜플을 값으로 저장하는 해시 맵
# - WSM에서 if 분기를 늘리는 대신 이 표만 확장하면 신규 질환 대응 가능 (확장성/유지보수성 ↑)
# - "비만"은 체중 기반(is_obese)으로 별도 처리하므로 이 표에서 제외
DISEASE_FOOD_MAP = {
    "관절염": ("has_joint_supp", "관절염 특화 사료"),
    "심장병": ("has_heart_supp", "심장병 특화 사료"),
    "신장병 (콩팥병)": ("has_kidney_supp", "신장병 특화 사료"),
    "신장병": ("has_kidney_supp", "신장병 특화 사료"),
    "당뇨": ("has_diabetes_supp", "당뇨 관리 특화 사료"),
    "쿠싱증후군": ("has_cushing_supp", "쿠싱증후군 관리 특화 사료"),
    "갑상선 기능 저하증": ("has_thyroid_supp", "갑상선 기능 저하증 케어 사료"),
    "간질환": ("has_liver_supp", "간질환 케어 특화 사료"),
    "피부 알레르기": ("has_skin_supp", "피부 알레르기 케어 사료"),
    "식품 알레르기": ("has_food_allergy_supp", "식품 알레르기(저알러지) 특화 사료"),
    "안과 질환 (백내장 등)": ("has_eye_supp", "안과 질환(항산화) 케어 사료"),
    "치주 질환": ("has_dental_supp", "치주 질환(구강) 케어 사료"),
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
#     · 기저질환 특화 사료 매칭 (관절/심장/신장): +80점 (최우선)
#     · 연령 그룹 일치 (puppy/adult/senior):      +40점
#     · 체형(비만/저체중/정상) 적합성:             +15~25점
#     · 견종 크기별 키블 적합성:                   +10점 (기본)
# - 시간 복잡도: O(k) — k는 평가 기준 수(고정값이므로 사실상 O(1))
def calculate_wsm(profile, food):
    score = 0
    reasons = []
    conditions = profile.get("conditions", [])
    
    # [자료구조/알고리즘] 매핑 테이블 기반 질환 매칭 — 보유 질환마다 사료 플래그를 O(1) 조회
    # - matched_flags: 같은 플래그를 가리키는 중복 키("신장병"/"신장병 (콩팥병)") 중복 가점 방지
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
