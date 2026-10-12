from __future__ import annotations

from datetime import datetime, timedelta

SUBJECTS: dict[str, tuple[str, ...]] = {
    "backend": (
        "FastAPI의 DB 연결 풀 크기", "PostgreSQL 복합 인덱스의 컬럼 순서",
        "Python 비동기 작업의 타임아웃", "백엔드 API의 중복 요청 처리",
        "데이터베이스 트랜잭션의 경계", "FastAPI 페이지네이션의 커서 설계",
        "Python worker의 재시도 간격", "PostgreSQL의 느린 쿼리 실행 계획",
        "백엔드 캐시의 만료 정책", "데이터베이스 변경 이벤트의 순서 보장",
    ),
    "travel": (
        "제주 동쪽 해안의 버스 여행", "서울 성곽길의 일몰 사진 산책",
        "부산 골목 맛집을 찾아가는 여행", "비 오는 날의 제주 실내 여행",
        "강릉 바다 사진을 찍는 당일 여행", "서울 시장 맛집을 둘러보는 반나절 여행",
        "경주 유적지 사이를 걷는 여행", "전주 골목 사진을 남기는 주말 여행",
        "제주 혼자 여행의 숙소 위치", "서울 근교 기차 여행의 짐 꾸리기",
    ),
    "fitness": (
        "러닝 초보의 주간 거리 배분", "집에서 하는 하체 근력 운동",
        "아침 운동 전 준비 시간", "비 오는 날 실내 러닝 훈련",
        "직장인의 짧은 점심 운동", "근력 훈련 사이의 휴식일",
        "러닝 기록과 몸 상태의 함께 기록", "맨몸 운동 동작을 익히는 순서",
        "주말 등산을 위한 근력 훈련", "꾸준한 운동을 위한 일정 관리",
    ),
    "music": (
        "기타 코드 전환 연습", "작은 공연장의 라이브 음악 감상",
        "재즈 앨범의 첫 감상", "기타 리듬 스트로크 녹음",
        "출근길 음악 목록 구성", "인디 밴드 공연의 곡 순서",
        "영화 음악의 반복 선율", "어쿠스틱 앨범의 악기 소리",
        "기타 합주에서 박자 맞추기", "주말 공연 감상 기록",
    ),
    "finance": (
        "가계부의 고정 지출 분류", "첫 월급의 저축 계획",
        "식비 예산의 주간 배분", "여행 경비를 위한 저축 기록",
        "가계부에 구독료 모아 보기", "이사 준비 예산의 항목 나누기",
        "경제 기사 속 물가 지표 읽기", "월말 가계부와 예산 비교",
        "비정기 지출을 위한 저축 목표", "취미 생활 예산의 우선순위",
    ),
}

STYLES: dict[str, tuple[str, ...]] = {
    "backend": (
        "{subject} 때문에 작은 재현 코드를 만들었습니다. 정상 요청만 보다가 실패 상황을 넣으니 놓친 조건이 보였어요.",
        "{subject}를 바꾸기 전에 어떤 지표부터 보시나요? 평균 응답 시간과 p95가 달라 판단 기준이 궁금합니다.",
        "오늘의 개발 메모는 {subject}입니다. 설정값 하나만 바꾸고 요청 수를 고정해 전후 로그를 비교해 보려 해요.",
        "스터디에서 {subject}를 설명하다가 막혔습니다. 개념은 알겠는데 실제 장애 사례와 연결하는 연습이 더 필요하네요.",
    ),
    "travel": (
        "이번 주말 계획은 {subject}입니다. 장소를 많이 넣기보다 한 구역에서 천천히 머무는 일정으로 적어 봤어요.",
        "{subject}를 준비 중이에요. 차 없이 이동할 때 놓치기 쉬운 점이나 여유 있게 잡아야 할 구간이 있을까요?",
        "{subject} 후기를 메모해 봅니다. 계획한 곳을 다 보기보다 잠깐 쉬었던 시간이 더 기억에 남았어요.",
        "친구와 {subject} 일정을 짜고 있어요. 저는 사진, 친구는 식사가 중요해서 이동 시간을 줄이는 쪽으로 맞추고 있습니다.",
    ),
    "fitness": (
        "이번 주 운동 기록의 주제는 {subject}입니다. 남의 수치와 비교하기보다 내가 꾸준히 했는지부터 적어 봤어요.",
        "{subject}를 일정에 넣으려는데 야근이 생기면 자꾸 밀리네요. 바쁜 주에는 어떻게 계획을 조정하시나요?",
        "{subject}를 기록할 표를 만들었어요. 시간과 횟수 옆에 피로도와 휴식 여부도 남겨 보려고 합니다.",
        "운동 모임에서 {subject} 이야기를 나눴습니다. 같은 계획도 사람마다 다르게 느낀다는 점이 인상적이었어요.",
    ),
    "music": (
        "오늘은 {subject}에 시간을 썼어요. 처음에는 지나쳤던 부분을 다시 들으니 새롭게 느껴지는 구간이 있네요.",
        "{subject}를 즐기는 분들은 어떤 점에 집중하시나요? 저는 멜로디를 먼저 듣지만 리듬에도 귀를 기울여 보고 싶어요.",
        "{subject} 메모를 남겼습니다. 좋았다는 말만 쓰지 않고 기억에 남은 소리와 순간을 구체적으로 적어 봤어요.",
        "친구와 {subject} 이야기를 했어요. 같은 음악을 두고 서로 다른 장면을 떠올려 감상 목록을 바꿔 보기로 했습니다.",
    ),
    "finance": (
        "이번 달에는 {subject}부터 정리해 봤어요. 숫자를 적기 전에는 몰랐던 작은 지출이 눈에 들어옵니다.",
        "{subject}를 정리할 때 항목을 얼마나 세분화하시나요? 너무 자세하면 기록을 오래 유지하기 어려워 고민이에요.",
        "오늘의 생활비 메모는 {subject}입니다. 예상 금액과 실제 금액을 나란히 놓고 차이가 난 이유를 적어 보려 해요.",
        "가족과 {subject}를 함께 이야기했어요. 같은 금액이라도 중요하게 생각하는 용도가 달라 우선순위부터 맞췄습니다.",
    ),
}


SUBJECTS.update({
    "ai_dev": (
        "Python으로 만드는 RAG 검색", "LLM 응답의 JSON 검증", "임베딩 모델의 검색 품질 비교",
        "AI 코드 도우미의 테스트 작성", "LangGraph 작업의 중단과 재개", "프롬프트 변경 전후 평가",
        "AI API의 호출 비용 기록", "벡터 검색의 후보 개수 조절", "AI 서비스의 응답 캐시", "LLM 실패 시 대체 응답",
    ),
    "travel_video": (
        "제주 여행 브이로그의 촬영 동선", "서울 골목 여행 영상의 장면 구성", "부산 여행 유튜브의 현장 소리",
        "비 오는 여행지에서 카메라 보호", "기차 여행 브이로그의 자막 편집", "혼자 여행하며 삼각대 사용",
        "여행 영상에서 장소 정보 전달", "해외 여행 브이로그의 짐 줄이기", "여행 유튜브 썸네일 사진 선택", "여행 경비를 영상으로 기록",
    ),
    "fitness_food": (
        "아침 운동 뒤 간단한 식사 준비", "러닝하는 날의 도시락 구성", "근력 운동과 식사 기록",
        "바쁜 날 운동 식단의 장보기", "운동 후 두부와 달걀 요리", "주말 운동을 위한 밀프렙",
        "운동일과 휴식일의 식사 관찰", "러닝 전후 수분 섭취 기록", "운동 식단에 채소 더하기", "외식하는 날의 운동 식사 계획",
    ),
})
for topic in ("ai_dev", "travel_video", "fitness_food"):
    STYLES[topic] = (
        "오늘은 {subject}를 해봤어요. 직접 해보니 준비 과정에서 놓친 부분을 알게 되어 기록합니다.",
        "{subject}를 해본 분들은 어떻게 시작하셨나요? 다음에 시도할 방법을 비교하고 있어요.",
        "이번 주에는 {subject}에 집중했습니다. 진행 과정과 결과를 짧은 메모로 남겨 봅니다.",
        "친구와 {subject}에 대해 이야기했어요. 서로의 경험이 달라 다음에는 다른 방법도 시도하려고 합니다.",
    )


def post_body(topic: str, ordinal: int) -> str:
    subjects = SUBJECTS[topic]
    styles = STYLES[topic]
    if not 0 <= ordinal < len(subjects) * len(styles):
        raise ValueError("post ordinal must be between 0 and 39")
    subject = subjects[ordinal % len(subjects)]
    return styles[ordinal // len(subjects)].format(subject=subject)


def post_created_at(post_id: int, reference: datetime, group_size: int = 5) -> datetime:
    if group_size < 1 or not 1 <= post_id <= 40 * group_size:
        raise ValueError("post id must fit the topic groups")
    if reference.utcoffset() is None:
        raise ValueError("reference must include a timezone")
    if post_id <= group_size:
        return reference - timedelta(hours=48, minutes=1)
    if post_id <= 2 * group_size:
        return reference - timedelta(hours=48)
    if post_id <= 3 * group_size:
        return reference - timedelta(hours=47, minutes=59)
    if post_id <= 4 * group_size:
        return reference + timedelta(minutes=1)
    return reference - timedelta(minutes=post_id - 4 * group_size)
