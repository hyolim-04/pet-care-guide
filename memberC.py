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
# - 내부 노드(Internal Node): 질환 카테고리 (소화기계질환, 호흡기계질환 등)
# - 리프 노드(Leaf Node): 개별 질환 (급성위염, 급성장염 등) — symptom 키 보유
# - DFS 탐색의 입력 데이터로 사용됨
# -Input 데이터 출처: 대한민국 정책브리핑 누리집에 공개된 농촌진흥청 국립축산과학원의 2018년 11월 13일 자 공식 브리핑 자료인 '동물병원 진료 기록 기반 반려견 내원 이유 분석' 보도자료 및 첨부파일(hwp)을 프로젝트 양식에 맞게 학술적으로 자체 정제
diseaseHierarchy = {
    "name": "반려동물질환",
    "children": [
        {
            "name": "소화기계질환",
            "children": [
                { "name": "급성위염", "symptom": "구토", "danger": "보통", "steps": ["1단계: 1-3세 및 전 연령대 다발성 구토 증상 확인 시 위장 휴식을 위해 12시간 금식", "2단계: 구토로 인한 탈수를 막기 위해 미온수를 종이컵 반 컵 분량으로 수시 급여", "3단계: 증상이 가라앉으면 소화가 잘되는 처방식 유동식(죽)을 소량 배식", "4단계: 지속적인 구토는 전염성 장염의 신호일 수 있으므로 추가 역학 조사 필요"] },
                { "name": "급성장염", "symptom": "설사", "danger": "보통", "steps": ["1단계: 1세 미만 영유아기 다발성 물설사 확인 시 대변으로 유실된 수분 즉시 보충", "2단계: 장내 유익균 회복과 장 점막 보호를 돕는 동물용 정품 유산균 소량 급여", "3단계: 파보 및 코로나 전염성 바이러스 징후 체크를 위해 분변 상태 정밀 스캔", "4단계: 변에 피가 섞여 나오는 혈변이거나 악취가 심해지면 치명적이므로 즉시 병원 내원"] },
                { "name": "이물섭식", "symptom": "침흘림", "danger": "위험", "steps": ["1단계: 통계 전체 16위인 이물섭식을 반영하여, 입 주변 잔여물 확인 및 억지로 빼내지 않기", "2단계: 플라스틱이나 뼈 등 장폐색을 유발할 수 있는 위험 물질인지 즉시 파악", "3단계: 독성 물질이 아니라면 경과를 지켜보되 구토를 동반하면 즉시 내원", "4단계: 침흘림과 함께 호흡 곤란 발생 시 기도를 막은 응급 상황이므로 하임리히법 시도 후 이송"] }
            ]
        },
        {
            "name": "피부및외이염질환",
            "children": [
                { "name": "알레르기성피부염", "symptom": "몸긁음", "danger": "보통", "steps": ["1단계: 전 연령대 부동의 상위권인 피부염 확인 시 환부를 핥지 못하도록 즉시 넥카라 착용", "2단계: 실내 집먼지진드기, 곰팡이성 균사 등 환경적 유해 요인 차단 및 청소", "3단계: 사료 첨가물이나 계절 변화로 인한 소양증 유발 알러젠 반응 스캔", "4단계: 스테로이드제나 소양증 완화제 장기 복용 시 호르몬 불균형 부작용 주의"] },
                { "name": "외이도염", "symptom": "귀긁음", "danger": "낮음", "steps": ["1단계: 4살 이후 급증하는 외이염 특성 고려하여 내부 통풍 위해 귀를 열고 환기", "2단계: 귀 소양증을 유발하는 세균성 또는 말라세치아 진드기 감염 여부 귀지 상태 체크", "3단계: 단백질 알러지 반응으로 인한 이도 내 발적 및 가려움증 강력 의심", "4단계: 무리한 면봉 사용은 이도 피부 손상의 부작용 및 농피증을 유발하므로 금지"] },
                { "name": "말라세치아감염", "symptom": "발핥음", "danger": "보통", "steps": ["1단계: 통계 10위 말라세치아 감염 지표 반영, 습한 환경에서 곰팡이균이 증식하므로 발바닥 건조 유지", "2단계: 산책 후 발을 씻긴 뒤 물기가 남지 않도록 완벽하게 드라이", "3단계: 발핥음 행동이 심해지면 넥카라를 씌워 2차 피부염 감염 방지", "4단계: 만성적인 소양증과 악취 동반 시 전용 약용 샴푸 처방 및 알러지 관리 병행"] }
            ]
        },
        {
            "name": "호흡기계질환",
            "children": [
                { "name": "상부호흡기계질환", "symptom": "기침", "danger": "위험", "steps": ["1단계: 노령기 전후 상부호흡기질환 발생 시 흥분을 가라앉히기 위해 실내 어둡게 조성", "2단계: 기관지 목에 압박을 주는 목줄 대신 가슴줄(하네스)로 전면 교체하여 자극 완화", "3단계: 바이러스성 감염 또는 기관지 협착에 의한 세포 독성 및 호흡 곤란 증세 의심", "4단계: 기침과 함께 청색증이 동반될 경우 치명적인 응급 상태이므로 신속 이송 요망"] }
            ]
        },
        {
            "name": "안과질환",
            "children": [
                { "name": "결막염", "symptom": "눈충혈", "danger": "낮음", "steps": ["1단계: 통계 상위 15위 결막염 지표 반영하여 박테리아 번식 막기 위해 멸균 거즈로 세정", "2단계: 안구 삼출물과 눈물 고임으로 인해 주변 피부가 짓무르지 않게 털 정리", "3단계: 결막 부종이나 각막 상처로 인한 부작용일 수 있으므로 안구 정밀 검사 권장", "4단계: 안과 전용 점안액 투여 시 정량 및 오투약 여부를 수의사 처방에 따라 검증"] }
            ]
        },
        {
            "name": "구강및근골격계질환", 
            "children": [
                { "name": "치주염", "symptom": "입냄새", "danger": "보통", "steps": ["1단계: 7세 이상 다발성 치주염 지표 반영하여 전용 치약으로 구강 내 세균 억제 칫솔질", "2단계: 치석 및 치태 제거를 돕는 기능성 덴탈 껌 및 딱딱한 제형의 사료 급여", "3단계: 치태가 딱딱한 치석으로 고착되면 독성 염증 반응 및 식욕부진 유발 가능", "4단계: 잇몸 통증에 의한 전신 염증 합병증 부작용 동반 시 전신마취 후 스케일링 요망"] },
                { "name": "슬개골탈구파행", "symptom": "뒷다리절뚝", "danger": "위험", "steps": ["1단계: 통계 상위권 파행 지표 반영하여 관절에 하중이 가해지는 과격한 행동 전면 중단", "2단계: 소형견 다발성 유전 질환 특성상 침대나 소파 아래 미끄럼 방지 매트 시공 필수", "3단계: 관절 주머니 염증 부작용을 예방하기 위해 철저한 체중 감량으로 하중 분산 유도", "4단계: 다리를 들고 절뚝거리는 파행 증상이 고착화될 경우 외과적 관절 수술 권장"] }
            ]
        },
        {
            "name": "노령기만성기저질환",
            "children": [
                { "name": "급성신부전", "symptom": "포도먹음", "danger": "위험", "steps": ["1단계: 10세 이상 상위권 신부전 지표 반영하며 포도 성분은 치명적인 급성 신장 독성을 유발함", "2단계: 흡수되기 전 골든타임 2시간 이내라면 즉시 동물병원 내원하여 구토 유발 처치 진행", "3단계: 체내 흡수 시 혈중 수치 통제를 위해 최소 48시간 이상 연속 정맥 수액 처치 필수", "4단계: 소변을 아예 보지 않는 무뇨증 부작용 발생 시 예후가 극도로 불량하므로 신속 이송"] },
                { "name": "심장질환실신", "symptom": "기절", "danger": "위험", "steps": ["1단계: 7세 이상 및 13-15세 3위 심장질환 지표 반영하며 순간적 뇌 혈류 차단으로 발생함", "2단계: 아이가 의식을 잃고 쓰러지면 목을 곧게 펴서 호흡 기도를 확보하고 신체 체온 유지", "3단계: 만성 심장 약물 복용을 임의 중단하거나 오투약 시 나타나는 치명적 부작용 징후 의심", "4단계: 폐에 물이 차는 폐수종 독성 합병증으로 진행되기 전 24시 응급 동물병원으로 이동"] },
                { "name": "유선종양", "symptom": "가슴몽우리", "danger": "위험", "steps": ["1단계: 10-12세 11위 유선종양 지표 반영, 복부나 가슴 주변 몽우리 발견 시 만지는 것 중단", "2단계: 중성화하지 않은 암컷 노령견에게 치명적이므로 정기적인 촉진 검사 필수", "3단계: 악성 종양(암)일 확률이 높으므로 발견 즉시 동물병원에서 조직 검사 진행", "4단계: 수술 후 전이 여부를 모니터링하고 면역력 저하 부작용 주의"] },
                { "name": "부신피질기능항진증", "symptom": "배나옴", "danger": "보통", "steps": ["1단계: 10-12세 14위 부신피질기능항진증(쿠싱증후군) 지표 반영, 다음다뇨 및 배가 빵빵해지는 증상 관찰", "2단계: 노령견에게 다발하는 호르몬 질환이므로 단순 비만으로 오인하지 않도록 주의", "3단계: 확진 시 평생 약물 관리가 필요하므로 정기적인 혈액 검사 필수", "4단계: 임의로 약물 복용을 중단할 경우 호르몬 불균형 쇼크 부작용이 올 수 있으므로 복약 지도 준수"] }
            ]
        }
    ]
}

# [자료구조] 동적 배열(List) — 자동완성 및 Trie 삽입에 사용되는 증상 키워드 목록

symptomKeywords = [
    "구토", "설사", "몸긁음", "귀긁음", "기침", "눈충혈", "입냄새", 
    "뒷다리절뚝", "포도먹음", "기절", "침흘림", "발핥음", "가슴몽우리", "배나옴"
]

# [자료구조] 선형 문자 배열 — KMP 문자열 탐색용 커뮤니티 후기 원문 데이터
# ==============================================================================
# [데이터 기획 및 설계 배경 명세]
# 본 communityReviews 데이터 세트는 아래의 3가지 핵심 기준을 기반으로 역설계된 정밀 테스트 데이터 세트
# 1. 수의학적 통계 기반: 농림축산검역본부 논문 통계의 연령대별 다발성 질환 리스크 지표(영유아기 소화기 질환, 
#    성숙기 피부/외이염, 노령기 심장/신장 기저질환)를 스토리텔링 형식으로 재구성하여 반영
# 2. KMP 알고리즘 검증: 본 프로그램의 핵심 엔진인 KMP 문자열 매칭 알고리즘이 증상어(keyword)와 
#    위험 키워드 풀(부작용, 독성, 알러지)을 교차 검증(AND 조건 필터링)할 수 있도록 문맥 내에 조건식을 매립
# 3. 데이터 리얼리티 확보: 국내 최대 반려견 커뮤니티 '강사모'의 실제 유저들이 사용하는 구어체 텍스트 패턴과 
#    감정적 어조를 접목하여 데이터의 도메인 실무 완성도를 극대화
# ==============================================================================
communityReviews = [
    "우리 아이 기침 증상이 통계에 나온 상부호흡기계 바이러스 독성 감염 때문일 수 있다고 해서 식겁했네요.",
    "사료 성분을 잘못 보아 닭고기 알러지 반응으로 결막염과 눈충혈 증상이 펑펑 나서 사료 바로 바꿨어요.",
    "감기약 처방 후 갑자기 구토 현상이 생겨 약물 부작용인 줄 알고 놀랐는데 급성위염 초기 증세였네요.",
    "강아지가 사료를 너무 급하게 먹었는지 가볍게 구토 증세를 보였는데 소화제 먹이고 금식하니 금방 생생해졌어요.",
    "요즘 날씨가 건조해서 그런가 눈가에 결막염 자국과 눈충혈이 조금 보이길래 깨끗한 거즈로 케어 중입니다.",
    "저희 집 늙은 포메 아이는 7살 넘어가면서 상부호흡기계 기침 현상이 부쩍 잦아져서 영양제 알아보고 있어요.",
    "겨울철 환기 시킬 때 실내가 추워지면 아주 일시적으로 가벼운 기침 증상을 하기도 하던데 보일러 트니 괜찮네요.",
    "급성 위염으로 심하게 구토 하던 아이인데 대처 가이드대로 하니 다행히 완치되었습니다.",
    "갑자기 물 설사 증세를 무지막지하게 하길래 장염 유산균 부작용인가 싶어 병원 가보려고요.",
    "포메 슬개골 수술 후 파행 증상과 뒷다리절뚝 거리는 부작용 때문에 가슴이 찢어집니다. 다들 미끄럼 매트 꼭 까세요.",
    "아이가 식탁 위에 포도먹음 사고를 쳐서 급성 신부전 독성 올라와 응급실 가서 밤새 수액 맞고 피 말렸습니다.",
    "약물 부작용 합병증 무섭네요. 심장질환 약 먹던 노령견 아이가 아침에 켁켁대다가 툭 기절 하더라구요.",
    "산책하다가 이상한 걸 주워먹고 침흘림 증상을 보여서 독성 물질일까 봐 응급실 다녀왔어요.",
    "강아지가 계속 발핥음 행동을 해서 연고를 발라줬는데 알러지 부작용인지 더 심해져서 말라세치아 진단받았네요.",
    "중성화 안 한 암컷인데 가슴몽우리 만져져서 유선종양 수술했어요. 마취 부작용 생길까 봐 너무 무서웠네요.",
    "노령견 배나옴 증상이 그냥 살찐 건 줄 알았는데 쿠싱증후군 약물 부작용일 수도 있다고 해서 검사받으려고요.",
    "강아지가 사료를 바꾸고 나서 심한 몸긁음 증상을 보이길래 식이성 알러지인 줄 알았는데 병원 가봐야겠어요.",
    "외이도염 때문에 처방받은 귀약을 넣었더니 아이가 심하게 귀긁음 증상을 보여서 독성 반응 올까 봐 당장 중단했습니다.",
    "노령견 입냄새가 너무 심해져서 치주염인 줄 알았는데, 신장 약물 장기 복용 부작용으로 인한 합병증일 수 있다고 하네요."
]
# [자료구조] 해시 맵(Dictionary) — 기저질환 → 위험 증상 매핑 테이블
# - 기저질환명(문자열)을 키로, 관련 증상 리스트를 값으로 저장
# - 조회 시간: O(1) 평균
CHRONIC_DISEASE_MAPPING = {
    "심장병": ["기침"],
    "신장병": ["포도먹음"],
    "관절염": ["뒷다리절뚝"],
    "알레르기": ["몸긁음", "귀긁음", "눈충혈", "발핥음"],
    "호르몬질환": ["배나옴"],
    "종양": ["가슴몽우리"]
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
# 1-2. 알고리즘: 한글 초성 분리 및 최소 편집 거리 (Levenshtein Distance) 오타 교정
# - 사용자가 검색창에 초성만 입력하거나(예: 'ㄱㅌ' -> '구토') 오타를 쳤을 때(예: '구톤' -> '구토')
#   이를 실시간으로 감지하고 교정하여 자동완성 및 정밀 분석을 보정하는 예외 처리 엔진
# - 초성 분리: 한글 유니코드 공식을 역산하여 초성 자소 매핑 (시간 복잡도: O(L))
# - 편집 거리: 디내믹 프로그래밍(DP)을 통해 두 문자열 간의 최소 변경 횟수 산출
#   (시간 복잡도: O(m × n) — m, n은 두 단어의 길이)
# ==============================================================================

# [알고리즘] 한글 초성 추출 함수 — 음절 문자열을 초성 자소 체계로 전형 변환

## 1. 초성만 쳤을 때를 위한 추출기
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    result = []
    for char in text:
        if '가' <= char <= '힣':
            char_code = ord(char) - 44032
            chosung_idx = char_code // 588
            result.append(CHOSUNG_LIST[chosung_idx])
        else:
            result.append(char)
    return "".join(result)

# 2. [핵심 엔진] "이" -> "ㅇㅣ", "입" -> "ㅇㅣㅂ" 처럼 타이핑 진행 상태를 분리해주는 함수
def decompose_hangul(text):
    CHOSUNG = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    JUNGSUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
    JONGSEONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"
    result = ""
    for char in text:
        if '가' <= char <= '힣':
            code = ord(char) - 44032
            # 종성이 없는 경우(공백)를 제거하여 순수 입력 상태와 완벽 매칭
            result += CHOSUNG[code // 588] + JUNGSUNG[(code % 588) // 28] + JONGSEONG[code % 28].strip()
        else:
            result += char
    return result

# 3. 오타 허용 엔진
def get_levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return get_levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
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
        
    matches = []
    query_chosung = get_chosung(query)
    query_jamo = decompose_hangul(query)
    
    for kw in symptomKeywords:
        kw_chosung = get_chosung(kw)
        kw_jamo = decompose_hangul(kw)
        
        # 조건 1. 초성 완벽 접두사 매칭 (in 대신 startswith 사용: 'ㅇ'이 '몸긁음'을 잡는 버그 차단)
        if query_chosung == query and kw_chosung.startswith(query_chosung):
            matches.append(kw)
        
        # 조건 2. 한글 자모 단위 진행형 매칭 ('이'(ㅇㅣ) 치는 중일 때 '입냄새'(ㅇㅣㅂ) 잡아줌)
        elif kw_jamo.startswith(query_jamo):
            matches.append(kw)
            
        # 조건 3. 한 글자 삐끗한 오타 교정 매칭 ('임냄새' 쳤을 때 '입냄새' 잡아줌)
        elif get_levenshtein_distance(query, kw) <= 1:
            matches.append(kw)
            
    # 중복 제거 후 깔끔하게 프론트엔드로 전달
    final_matches = list(dict.fromkeys(matches))
    return jsonify({'matches': final_matches})
    
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
