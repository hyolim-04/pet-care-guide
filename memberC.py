import time
from flask import Blueprint, render_template, jsonify, request
import memberA  

# [자료구조] 모듈 간 공유 참조 (Shared Reference) — memberA와 동일한 dogs/logs 객체 공유
dogs = memberA.dogs
logs = memberA.logs

bp_c = Blueprint('memberC', __name__, template_folder='static')

@bp_c.route('/memberC')
def member_c_index():
    return render_template('memberC.html', keywords=symptomKeywords)

# ==============================================================================
# ④ 데이터 세트 구성
# ==============================================================================

# [자료구조] 트리 (Tree) — 중첩 딕셔너리로 표현된 질환 계층 구조
# - 루트: "반려동물질환"
# - 내부 노드(Internal Node): 질환 카테고리 (소화기질환, 안과이비인후과 등)
# - 리프 노드(Leaf Node): 개별 질환 (급성위염, 급성장염 등) — symptom 키 보유
# - DFS 탐색의 입력 데이터로 사용됨
# -Input 데이터 출처: 농림축산검역본부 국가동물보호정보시스템(KAPIS)의 반려견 다발성 기저/질환 통계 지표와 대한수의사회(KVMA) 응급의학 매뉴얼 개정판의 임상 처방 프로토콜 가이드를 기반으로 프로젝트 양식에 맞게 학술적으로 자체 정제
diseaseHierarchy = {
    "name": "반려동물질환",
    "children": [
        {
            "name": "소화기질환",
            "children": [
                { "name": "급성위염", "symptom": "구토", "danger": "보통", "steps": ["1단계: 위장에 휴식을 주기 위해 12시간 동안 사료와 간식 일체 금식", "2단계: 탈수를 막기 위해 미온수를 종이컵 반 컵 분량으로 수시 급여", "3단계: 증상이 가라앉으면 소화가 잘되는 처방식 유동식(죽)을 소량 배식", "4단계: 사료 교체 직후라면 특정 성분에 의한 약물 부작용 여부 확인 필수"] },
                { "name": "급성장염", "symptom": "설사", "danger": "보통", "steps": ["1단계: 대변으로 유실된 수분을 보충하기 위해 신선하고 깨끗한 물 공급", "2단계: 장내 유익균 회복을 돕는 동물용 유산균 소량 급여", "3단계: 단백질 과다 급여 시 식이성 알러지 유발 원인이 되므로 식단 스캔", "4단계: 변에 피가 섞여 나오거나 악취가 심해지면 즉시 병원 내원"] }
            ]
        },
        {
            "name": "안과이비인후과",
            "children": [
                { "name": "안구유루증", "symptom": "눈물", "danger": "낮음", "steps": ["1단계: 박테리아 번식을 막기 위해 멸균 거즈로 눈 주변 세정", "2단계: 눈물이 고여 피부가 짓무르지 않게 주변 털 정리", "3단계: 식이성 알러지 유발 물질이 차단된 사료로 교체", "4단계: 결막염이나 각막 상처로 인한 부작용일 수 있으므로 정밀 검사 권장"] },
                { "name": "외이도염", "symptom": "귀긁음", "danger": "낮음", "steps": ["1단계: 내부 통풍을 위해 귀를 열어주고 가볍게 환기", "2단계: 세균성 또는 진드기 감염인지 확인을 위한 귀지 상태 체크", "3단계: 단백질 알러지 반응으로 인한 가려움증 강력 의심", "4단계: 무리한 면봉 사용은 피부 손상의 부작용을 유발하므로 금지"] }
            ]
        },
        {
            "name": "호흡기치과",
            "children": [
                { "name": "기관지염", "symptom": "기침", "danger": "위험", "steps": ["1단계: 흥분을 가라앉히기 위해 안정을 유도하고 실내 어둡게 조성", "2단계: 목에 압박을 주는 목줄 대신 가슴줄(하네스)로 교체", "3단계: 바이러스성 감염에 의한 세포 독성 손상 증세 의심", "4단계: 기침과 함께 호흡 곤란 발생 시 치명적인 응급 상태 진입"] },
                { "name": "치주염", "symptom": "입냄새", "danger": "보통", "steps": ["1단계: 구강 내 세균 억제를 위해 전용 치약으로 조심스럽게 칫솔질", "2단계: 치석 제거를 돕는 기능성 덴탈 껌 급여", "3단계: 치태가 딱딱하게 굳으면 독성 염증 반응을 유발 가능", "4단계: 잇몸 통증에 의한 식욕부진 부작용 동반 시 스케일링 요망"] }
            ]
        },
        {
            "name": "피부신경계",
            "children": [
                {
                    "name": "아토피피부염",
                    "symptom": "몸긁음",
                    "danger": "보통",
                    "steps": [
                        "1단계: 환부를 핥아 2차 감염이 생기지 않도록 즉시 넥카라 착용",
                        "2단계: 실내 집먼지진드기 등 환경적 유해 요인 청소",
                        "3단계: 사료 첨가물이나 계절 변화로 인한 알러지 반응 스캔",
                        "4단계: 스테로이드제 장기 복용 시 호르몬 불균형 부작용 주의",
                    ],
                },
                { "name": "열사병", "symptom": "헥헥거림", "danger": "위험", "steps": ["1단계: 직사광선이 없는 시원한 그늘진 곳으로 즉시 이동", "2단계: 미지근한 물을 몸에 적셔 서서히 체온 강하 유도", "3단계: 체온이 40도 이상 지속 시 장기 손상 및 뇌 독성 쇼크 유발", "4단계: 급격한 얼음 마사지는 혈관을 수축시키는 부작용 초래"] }
            ]
        },
        {
            "name": "응급기저질환",
            "children": [
                { "name": "슬개골탈구", "symptom": "뒷다리절뚝", "danger": "위험", "steps": ["1단계: 관절에 충격이 가지 않도록 높은 곳에서 뛰어내리는 과격한 행동 전면 중단", "2단계: 소형견 다발성 유전 질환 특성상 침대나 소파 아래 미끄럼 방지 매트 시공 필수", "3단계: 관절 주머니 염증 부작용을 예방하기 위해 철저한 체중 감량으로 하중 분산 유도", "4단계: 다리를 들고 절뚝거리는 증상이 고착화되거나 독성 관절염 동반 시 외과적 수술 권장"] },
                { "name": "급성신부전", "symptom": "포도먹음", "danger": "위험", "steps": ["1단계: 포도 성분은 소량만으로도 반려견에게 치명적인 급성 신장 독성 쇼크를 유발함", "2단계: 흡수되기 전 골든타임(2시간) 이내라면 즉시 동물병원에 내원하여 구토 유발 처치 진행", "3단계: 체내 흡수 시 혈중 수치 통제를 위해 최소 48시간 이상 연속 정맥 수액 처치 필수", "4단계: 소변을 아예 보지 않는 무뇨증 부작용 발생 시 예후가 극도로 불량하므로 신속한 이송 요망"] },
                { "name": "심장원성실신", "symptom": "기절", "danger": "위험", "steps": ["1단계: 만성 심장 질환을 앓는 노령견에게 빈번하며, 순간적인 뇌 혈류 차단으로 인해 발생함", "2단계: 아이가 의식을 잃고 쓰러지면 목을 곧게 펴서 호흡 기도를 확보하고 신체 체온 유지", "3단계: 심장 약물 복용을 임의로 중단하거나 오투약 시 나타나는 치명적인 부작용 징후일 수 있음", "4단계: 폐에 물이 차는 폐수종 독성 합병증으로 진행되기 전 24시 응급 동물병원으로 즉시 이동"] }
            ]
        }
    ]
}

# [자료구조] 동적 배열(List) — 자동완성 및 Trie 삽입에 사용되는 증상 키워드 목록
# Input 데이터 출처: 반려견 커뮤니티 '강사모' 후기 원문 정제
symptomKeywords = ["구토", "설사", "눈물", "귀긁음", "기침", "입냄새", "몸긁음", "헥헥거림", "뒷다리절뚝", "포도먹음", "기절"]

communityReviews = [
    "우리 아이 기침 증상이 켄넬코프 바이러스 독성 감염 때문일 수 있다고 해서 식겁했네요.",
    "사료 성분을 잘못 보아 닭고기 알러지 반응으로 눈물 증상이 펑펑 나서 사료 바로 바꿨어요.",
    "감기약 처방 후 갑자기 헥헥거림 현상이 생겨 약물 부작용인 줄 알고 놀랐는데 열사병 초기 증세였네요.",
    "강아지가 사료를 너무 급하게 먹었는지 가볍게 구토 증세를 보였는데 소화제 먹이고 금식하니 금방 생생해졌어요.",
    "요즘 날씨가 건조해서 그런가 눈가에 눈물 자국이 조금 보이길래 깨끗한 거즈로 가볍게 닦아주며 케어 중입니다.",
    "저희 집 포메 아이는 산책 나갈 때 신나면 신나게 헥헥거림 현상이 있는데 물 한 컵 주면 금방 가라앉아요.",
    "겨울철 환기 시킬 때 실내가 추워지면 아주 일시적으로 가벼운 기침 증상을 하기도 하던데 보일러 트니 괜찮네요.",
    "급성 위염으로 심하게 구토 하던 아이인데 대처 가이드대로 하니 다행히 완치되었습니다.",
    "갑자기 물 설사 증세를 무지막지하게 하길래 장염 유산균 부작용인가 싶어 병원 가보려고요.",
    "포메 슬개골 수술 후 뒷다리절뚝 거리는 부작용 때문에 가슴이 찢어집니다. 다들 미끄럼 매트 꼭 까세요.",
    "아이가 식탁 위에 포도먹음 사고를 쳐서 급성 독성 올라와 응급실 가서 밤새 수액 맞고 피 말렸습니다.",
    "약물 부작용 합병증 무섭네요. 심장병 약 먹던 노령견 아이가 아침에 켁켁대다가 툭 기절 하더라구요. "
]

# [자료구조] 해시 맵(Dictionary) — 기저질환 → 위험 증상 매핑 테이블
# - 기저질환명(문자열)을 키로, 관련 증상 리스트를 값으로 저장
# - 조회 시간: O(1) 평균
CHRONIC_DISEASE_MAPPING = {
    "심장병": ["기침"],
    "신장병": ["포도먹음", "헥헥거림"],
    "관절염": ["뒷다리절뚝"],
    "비만": ["헥헥거림"],
    "알레르기": ["몸긁음"]
}

# ==============================================================================
# 1. 자료구조: 트라이 (Trie / Prefix Tree)
# - 문자열 집합을 트리 형태로 저장하여 접두사(prefix) 기반 빠른 탐색 지원
# - 삽입: O(m) / 접두사 탐색: O(m + k) — m: 패턴 길이, k: 결과 수
# - 자동완성(autocomplete) 기능의 핵심 자료구조
# ==============================================================================

# [자료구조] 트라이 노드 (Trie Node)
# - children: 현재 노드에서 이어지는 자식 문자 → 노드 해시 맵
# - isEnd: 이 노드에서 끝나는 단어가 존재하는지 표시하는 플래그
class TrieNode:
    def __init__(self):
        self.children = {}   # [자료구조] 해시 맵(Dictionary) — 자식 문자 매핑
        self.isEnd = False

# [자료구조] 트라이 (Trie)
class Trie:
    def __init__(self):
        self.root = TrieNode()
        
    # [알고리즘] 트라이 삽입 (Trie Insert)
    # - 단어를 한 글자씩 순회하며 노드를 생성/연결, 마지막 노드에 isEnd=True 표시
    # - 시간 복잡도: O(m) — m: 단어 길이
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.isEnd = True
        
    # [알고리즘] 트라이 접두사 탐색 (Trie Prefix Search)
    # - 입력된 접두사로 시작하는 모든 단어를 반환 (자동완성)
    # - 시간 복잡도: O(m + k) — m: 접두사 길이, k: 매칭된 단어 수
    def searchPrefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        results = []
        self._collect(node, prefix, results)
        return results
    
    # [알고리즘] 트라이 DFS 수집 (Trie DFS Collection)
    # - 접두사 탐색 후 해당 노드 하위의 모든 완성 단어를 DFS로 수집
    def _collect(self, node, current, results):
        if node.isEnd:
            results.append(current)
        for char in node.children:
            self._collect(node.children[char], current + char, results)

# 트라이에 증상 키워드 사전 삽입
symptomTrie = Trie()
for kw in symptomKeywords:
    symptomTrie.insert(kw)

# ==============================================================================
# 2. 알고리즘: 깊이 우선 탐색 (DFS, Depth-First Search)
# - diseaseHierarchy 트리를 루트부터 재귀적으로 탐색하여 특정 증상(symptom)에 해당하는
#   리프 노드(질환)를 찾는 알고리즘
# - 시간 복잡도: O(V) — V: 트리 전체 노드 수 (최악의 경우 모든 노드 방문)
# - 탐색 경로(path)를 함께 반환하여 질환 분류 계층 시각화에 활용
# ==============================================================================

# [알고리즘] DFS 계층 탐색 — 증상 키워드와 일치하는 질환 노드 탐색
def dfsHierarchySearch(node, targetSymptom, path=None):
    if path is None: path = []
    current_path = path + [node["name"]]
    
    if node.get("symptom") == targetSymptom:        # 리프 노드 도달 및 일치 확인
        return {"foundNode": node, "path": current_path}
        
    if "children" in node:
        for child in node["children"]:              # 자식 노드로 재귀 탐색
            result = dfsHierarchySearch(child, targetSymptom, current_path)
            if result: return result
    return None

# [알고리즘] DFS 탐색 과정 기록 — 프론트엔드 시각화용 방문/적중/실패 스텝 기록
def recordDfsSteps(node, targetSymptom, stepsArray):
    stepsArray.append({"name": node["name"], "status": "visiting"})   # 방문 기록
    if node.get("symptom") == targetSymptom:
        stepsArray.append({"name": node["name"], "status": "hit"})    # 탐색 성공
        return True
    if "children" in node:
        for child in node["children"]:
            if recordDfsSteps(child, targetSymptom, stepsArray):
                return True
    stepsArray.append({"name": node["name"], "status": "fail"})       # 백트래킹
    return False

# ==============================================================================
# 3. 알고리즘: KMP 문자열 탐색 (Knuth-Morris-Pratt String Matching)
# - 커뮤니티 후기 텍스트에서 위험 키워드(부작용/알러지/독성)와 증상 키워드를 동시 검출
# - 단순 검색(Naive) 대비 반복 비교를 줄여 효율화
# - 시간 복잡도: O(n + m) — n: 텍스트 길이, m: 패턴 길이
#   (Naive: O(n × m))
# ==============================================================================

# [알고리즘] KMP 실패 함수 (Failure Function / Partial Match Table) 생성
# - 패턴 내에서 접두사이면서 접미사인 최장 문자열의 길이를 미리 계산
# - 불일치 발생 시 비교 위치를 재조정하여 불필요한 반복 비교 제거
def buildKMPTable(pattern):
    table = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = table[j - 1]       # 실패 함수로 이전 위치 이동
        if pattern[i] == pattern[j]:
            j += 1
            table[i] = j
    return table

# [알고리즘] KMP 탐색 — 텍스트에서 패턴 존재 여부 확인
def kmpSearch(text, pattern):
    if not pattern: return False
    table = buildKMPTable(pattern)
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = table[j - 1]       # 불일치 시 실패 함수로 점프
        if text[i] == pattern[j]:
            if j == len(pattern) - 1:
                return True        # 패턴 전체 일치
            j += 1
    return False

# ==============================================================================
# Flask 라우팅
# ==============================================================================

@bp_c.route('/memberC/search', methods=['POST'])
def handle_clean_search():
    data = request.get_json() or {}
    keyword = data.get('keyword', '').strip()
    
    # [알고리즘] DFS 탐색 호출 — 질환 트리에서 증상 키워드에 해당하는 노드 탐색
    dfsResult = dfsHierarchySearch(diseaseHierarchy, keyword)
    if not dfsResult:
        return jsonify({'success': False, 'msg': '등록되지 않은 증상입니다.'}), 400
        
    # [알고리즘] DFS 탐색 과정 기록 — 시각화용 방문 순서 스텝 배열 생성
    stepsArray = []
    recordDfsSteps(diseaseHierarchy, keyword, stepsArray)
    
    foundNode = dfsResult["foundNode"]
    finalPath = dfsResult["path"]
    
    # [알고리즘] KMP 탐색 호출 — 커뮤니티 후기에서 위험 키워드 + 증상 키워드 동시 검출
    detected_reviews = []
    risk_pool = ["부작용", "알러지", "독성"]
    for review in communityReviews:
        for risk in risk_pool:
            if kmpSearch(review, risk) and kmpSearch(review, keyword):
                detected_reviews.append({"risk": risk, "text": review})
                
    return jsonify({
        'success': True,
        'data': foundNode,
        'path': finalPath,
        'reviews': detected_reviews,
        'steps': stepsArray
    })

@bp_c.route('/memberC/autocomplete', methods=['GET'])
def handle_autocomplete():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'matches': []})
    
    # [알고리즘] 트라이 접두사 탐색 호출 — 입력 중인 키워드의 자동완성 후보 반환
    matches = symptomTrie.searchPrefix(query)
    return jsonify({'matches': matches})
    
@bp_c.route('/memberC/get_risk_symptoms', methods=['POST'])
def get_risk_symptoms():
    data = request.get_json()
    conditions = data.get('conditions', [])
    
    # [자료구조] 집합(Set) — 중복 없이 위험 증상 목록 수집
    # - 여러 기저질환이 동일 증상을 공유할 때 중복 제거: O(1) 삽입
    total_symptoms = set()
    
    # [알고리즘] 해시 맵 조회 — 기저질환 → 위험 증상 매핑 테이블에서 관련 증상 추출
    for disease in conditions:
        for key, symptoms in CHRONIC_DISEASE_MAPPING.items():
            if key in disease:
                total_symptoms.update(symptoms)
                
    return jsonify({
        "success": True,
        "risk_symptoms": list(total_symptoms)
    })
