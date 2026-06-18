from flask import Blueprint, jsonify, send_from_directory
import memberA

# [자료구조] 모듈 간 공유 참조 (Shared Reference)
# - memberA의 dogs/logs 객체를 직접 참조(reference)하여 동일한 메모리 공간 공유
# - 복사가 아닌 참조이므로 memberA에서 데이터 변경 시 memberB에도 즉시 반영됨
dogs = memberA.dogs
logs = memberA.logs
bp_b = Blueprint('module_b', __name__)

# ════════════════════════════════════════════════════════════
#  [자료구조] 중첩 딕셔너리 + 리스트 (Nested Dictionary + List)
#  - 사이즈("small"/"medium"/"large")를 키로, 사료 객체 리스트를 값으로 저장
#  - 버킷(bucket) 구조: 탐색 범위를 O(전체→버킷크기)로 축소
#  - ※ 다채로운 결과를 위해 심장+관절, 신장+종양 등 복합 질환 케어 사료 대폭 추가!
# ════════════════════════════════════════════════════════════
FOOD_DATABASE = {
    "small": [
        {"id": 1,  "name": "소형견 심장 케어 처방식", "price": 38000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 2,  "name": "소형견 신장 처방식", "price": 40000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 3,  "name": "소형견 관절 튼튼 스몰바이트", "price": 25000, "age_target": "adult", "protein": "normal", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 4,  "name": "소형견 저알러지 가수분해 케어", "price": 34000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 5,  "name": "소형견 호르몬(당뇨/갑상선) 대사 케어", "price": 39000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 6,  "name": "소형견 항산화 종양 케어", "price": 41000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
        {"id": 7,  "name": "소형견 심장/신장 올인원 케어", "price": 42000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 8,  "name": "소형견 관절/종양 시니어 케어", "price": 37000, "age_target": "senior", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
        {"id": 9,  "name": "소형견 알러지/호르몬 통합 케어", "price": 36000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": True, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 10, "name": "퍼피 고단백 스몰", "price": 28000, "age_target": "puppy", "protein": "high", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 11, "name": "퍼피 소화/관절 튼튼", "price": 31000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 12, "name": "소형견 체중 관리 다이어트", "price": 22000, "age_target": "adult", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 13, "name": "소형견 데일리 유지용", "price": 19000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 14, "name": "소형견 심장/관절 라이프 서포트", "price": 45000, "age_target": "senior", "protein": "normal", "has_joint_supp": True, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 15, "name": "소형견 신장/종양 힐링 케어", "price": 48000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
    ],
    "medium": [
        {"id": 20, "name": "중형견 심장/신장 집중 케어", "price": 55000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 21, "name": "중형견 신장 저단백 처방식", "price": 52000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 22, "name": "중형견 체중 감량/관절 케어", "price": 51000, "age_target": "adult", "protein": "low", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 23, "name": "중형견 저알러지 가수분해 케어", "price": 53000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 24, "name": "중형견 호르몬(당뇨/갑상선) 대사 케어", "price": 52000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 25, "name": "중형견 항산화 종양 케어", "price": 54000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
        {"id": 26, "name": "중형견 심장/호르몬 밸런스", "price": 58000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 27, "name": "중형견 관절/알러지 듀얼 케어", "price": 56000, "age_target": "adult", "protein": "normal", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 28, "name": "중형견 종양/신장 프로텍트", "price": 59000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
        {"id": 29, "name": "중형견 고단백 액티브", "price": 47000, "age_target": "adult", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 30, "name": "미디엄 퍼피 성장 조절", "price": 46000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 31, "name": "미디엄 어덜트 유지용", "price": 45000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
    ],
    "large": [
        {"id": 40, "name": "대형견 심장/관절 시니어", "price": 72000, "age_target": "senior", "protein": "normal", "has_joint_supp": True, "has_heart_supp": True, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 41, "name": "대형견 신장 처방식", "price": 75000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 42, "name": "대형견 관절 특화 성견용", "price": 65000, "age_target": "adult", "protein": "normal", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 43, "name": "대형견 저알러지 가수분해 케어", "price": 71000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": True, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 44, "name": "대형견 호르몬(당뇨/갑상선) 대사 케어", "price": 70000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 45, "name": "대형견 항산화 종양 케어", "price": 73000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": True},
        {"id": 46, "name": "대형견 심장/신장 올인원 케어", "price": 76000, "age_target": "senior", "protein": "low", "has_joint_supp": False, "has_heart_supp": True, "has_kidney_supp": True, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 47, "name": "대형견 종양/호르몬 시니어 매니지먼트", "price": 78000, "age_target": "senior", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": True, "has_tumor_supp": True},
        {"id": 48, "name": "대형견 알러지/호르몬 통합 케어", "price": 72000, "age_target": "adult", "protein": "normal", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": True, "has_hormone_supp": True, "has_tumor_supp": False},
        {"id": 49, "name": "대형견 고단백 머슬 핏", "price": 68000, "age_target": "adult", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 50, "name": "라지 퍼피 튼튼 골격", "price": 62000, "age_target": "puppy", "protein": "high", "has_joint_supp": True, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": False, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
        {"id": 51, "name": "라지 라이트 다이어트", "price": 58000, "age_target": "adult", "protein": "low", "has_joint_supp": False, "has_heart_supp": False, "has_kidney_supp": False, "is_diet": True, "has_allergy_supp": False, "has_hormone_supp": False, "has_tumor_supp": False},
    ]
}

# ════════════════════════════════════════════════════════════
#  [자료구조] 질환별 우선순위 가중치 테이블 (Disease Weight Map)
#  - 기존 80점 일괄 부여에서 의학적 중증도(Severity) 기반 차등 배점으로 업그레이드
#  - 생명과 직결된 질환일수록 압도적인 점수를 주어 최우선으로 추천되게 함
# ════════════════════════════════════════════════════════════
DISEASE_WEIGHT_MAP = {
    "심장병":   {"flag": "has_heart_supp",   "score": 120, "label": "❤️ 심장(생명직결) 케어 특화"},
    "신장병":   {"flag": "has_kidney_supp",  "score": 120, "label": "💧 신장(생명직결) 케어 특화"},
    "종양":     {"flag": "has_tumor_supp",   "score": 100, "label": "🛡️ 종양(항산화/면역) 케어"},
    "호르몬질환": {"flag": "has_hormone_supp", "score": 85,  "label": "⚖️ 호르몬/대사 케어"},
    "알레르기": {"flag": "has_allergy_supp", "score": 70,  "label": "🌿 알레르기(저알러지) 케어"},
    "관절염":   {"flag": "has_joint_supp",   "score": 60,  "label": "🦴 관절(모빌리티) 케어"}
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
# - 다기준 의사결정(MCDM) 기법: 각 평가 기준에 가중 점수를 부여하고 합산
def calculate_wsm(profile, food):
    score = 0
    reasons = []
    conditions = profile.get("conditions", [])

    # [핵심 로직] 중증도 기반 차등 배점 적용
    # - matched_flags: 동일 플래그 중복 가점 방지 
    matched_flags = set()
    for cond in conditions:
        entry = DISEASE_WEIGHT_MAP.get(cond)
        if not entry:
            continue
        
        flag = entry["flag"]
        if flag not in matched_flags and food.get(flag):
            added_score = entry["score"]
            score += added_score
            reasons.append({"점수": added_score, "사유": entry["label"]})
            matched_flags.add(flag)

    # 연령/체형/크기 매칭은 기존 점수 로직 유지
    if profile["age_group"] == food["age_target"]:
        score += 40
        label = {"puppy": "퍼피 발달 맞춤 영양", "senior": "시니어 노화 방지/저단백"}.get(profile["age_group"], "성견 유지용 적합")
        reasons.append({"점수": 40, "사유": label})

    if profile.get("is_obese") and food["is_diet"]:
        score += 25
        reasons.append({"점수": 25, "사유": "비만 판정: 다이어트/저지방 특화"})
    elif profile.get("is_underweight") and food.get("protein") == "high" and not food["is_diet"]:
        score += 25
        reasons.append({"점수": 25, "사유": "저체중 판정: 고단백 영양 공급 특화"})
    elif not profile.get("is_obese") and not profile.get("is_underweight") and not food["is_diet"]:
        score += 15
        reasons.append({"점수": 15, "사유": "일반 체형 유지용"})

    score += 10
    size_kr = {"small": "소형", "medium": "중형", "large": "대형"}.get(profile["size"], "소형")
    reasons.append({"점수": 10, "사유": f"{size_kr}견 전용 알갱이(키블) 크기"})

    return score, reasons

# [알고리즘] 병합 정렬 (Merge Sort)
def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

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
        sorted_logs = sorted(dog_logs, key=lambda x: x["date"])
        latest_weight = sorted_logs[-1]["weight"]
        latest_activity = sorted_logs[-1]["activity"]

    mapped_activity = {"낮음": "low", "보통": "medium", "높음": "high"}.get(latest_activity, "medium")
    conditions = [c for c in dog["diseases"] if c != "없음"]
    age = dog["age"]
    age_group = "puppy" if age < 1 else "senior" if age >= 8 else "adult"
    size = dog.get("size") or ("small" if latest_weight <= 8 else "medium" if latest_weight <= 20 else "large")

    profile = {
        "name": dog["name"], "breed": dog["breed"], "age": age, "weight": latest_weight,
        "size": size, "activity": mapped_activity, "conditions": conditions,
        "age_group": age_group,
        "is_obese": check_obesity(size, latest_weight),
        "is_underweight": check_underweight(size, latest_weight)
    }

    target_bucket = FOOD_DATABASE.get(size, [])

    processed_foods = []
    for food in target_bucket:
        score, reasons = calculate_wsm(profile, food)
        f = food.copy()
        f["score"] = score
        f["reasons"] = reasons
        processed_foods.append(f)

    return jsonify({
        "profile": profile,
        "total_count": sum(len(v) for v in FOOD_DATABASE.values()),
        "bucket_count": len(target_bucket),
        "top3": merge_sort(processed_foods)
    })