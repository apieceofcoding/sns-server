from datetime import UTC, datetime, timedelta

from .db import connection

TOPICS = {
    "backend": "Python FastAPI PostgreSQL 백엔드 설계와 데이터베이스 실습",
    "travel": "서울 제주 여행 사진과 맛집 산책 기록",
    "fitness": "운동 러닝 건강 근력 훈련 기록",
    "music": "음악 기타 공연 앨범 감상",
    "finance": "저축 예산 가계부 경제 공부",
}


def seed():
    now = datetime.now(UTC)
    with connection() as conn:
        for user_id, interests in enumerate(list(TOPICS.values())[:3], 1):
            conn.execute(
                "INSERT INTO users(id,interests) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (user_id, interests),
            )
        for i in range(1, 201):
            topic = list(TOPICS)[i % 5]
            conn.execute(
                """INSERT INTO posts(id,author_id,body,topic,likes,created_at)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (
                    i,
                    10 + i % 20,
                    f"{TOPICS[topic]}: 오늘의 기록 {i}",
                    topic,
                    (i * 17) % 101,
                    now - timedelta(minutes=201 - i),
                ),
            )
    return {"users": 3, "posts": 200, "data": "synthetic"}
