from datetime import UTC, datetime

from sns_recommend.post_examples import post_body, post_created_at

from .db import source_connection

TOPICS = {
    "backend": "Python FastAPI PostgreSQL 백엔드 설계와 데이터베이스 실습",
    "travel": "서울 제주 여행 사진과 맛집 산책 기록",
    "fitness": "운동 러닝 건강 근력 훈련 기록",
    "ai_dev": "Python LLM RAG 임베딩과 AI 서비스 개발",
    "travel_video": "여행 브이로그 촬영 편집과 여행 유튜브 기록",
    "fitness_food": "운동 식단 러닝 식사와 밀프렙 기록",
}
READERS = {
    7: "Python 백엔드와 AI 개발, 데이터베이스와 RAG에 관심",
    8: "여행지와 여행 일정, 여행 유튜브와 브이로그에 관심",
    9: "운동과 러닝, 건강한 식단과 운동 후 식사에 관심",
}
USERS = {**dict(enumerate(TOPICS.values(), 1)), **READERS}


def seed():
    now = datetime.now(UTC)
    with source_connection() as conn:
        for user_id, interests in USERS.items():
            username = f"course-user-{user_id}"
            existing = conn.execute("SELECT username FROM users WHERE id=%s", (user_id,)).fetchone()
            if existing and existing["username"] != username:
                raise ValueError(f"seed user ID {user_id} is already used by another account")
            conn.execute(
                """INSERT INTO users(id,username,created_at,modified_at)
                VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (user_id, username, now, now),
            )
            conn.execute(
                """INSERT INTO user_interests(user_id,interests)
                VALUES (%s,%s) ON CONFLICT DO NOTHING""",
                (user_id, interests),
            )
        for i in range(1, 241):
            topic = list(TOPICS)[(i - 1) % 6]
            author_id = 1 + (i - 1) % 6
            body = post_body(topic, (i - 1) // 6)
            existing = conn.execute("SELECT user_id FROM posts WHERE id=%s", (i,)).fetchone()
            if existing and existing["user_id"] != author_id:
                raise ValueError(f"seed post ID {i} conflicts with existing data; use a fresh course database")
            conn.execute(
                """INSERT INTO posts(id,user_id,content,like_count,created_at,modified_at)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (i, author_id, body, (i * 17) % 101, post_created_at(i, now, group_size=6), now),
            )
        for table in ("users", "posts"):
            conn.execute(f"""SELECT setval(pg_get_serial_sequence('{table}', 'id'),
                GREATEST((SELECT max(id) FROM {table}),
                         nextval(pg_get_serial_sequence('{table}', 'id'))), true)""")
    return {"users": 9, "posts": 240, "data": "synthetic", "reference_time": now.isoformat()}
