from datetime import UTC, datetime

from sns_recommend.post_examples import post_body, post_created_at

from .db import source_connection

TOPICS = {
    "backend": "Python FastAPI PostgreSQL 백엔드 설계와 데이터베이스 실습",
    "travel": "서울 제주 여행 사진과 맛집 산책 기록",
    "fitness": "운동 러닝 건강 근력 훈련 기록",
    "music": "음악 기타 공연 앨범 감상",
    "finance": "저축 예산 가계부 경제 공부",
}


def seed():
    now = datetime.now(UTC)
    with source_connection() as conn:
        for user_id, interests in enumerate(list(TOPICS.values())[:3], 1):
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
        for i in range(1, 201):
            topic = list(TOPICS)[i % 5]
            author_id = 1 + (i - 1) % 3
            body = post_body(topic, (i - 1) // 5)
            existing = conn.execute("SELECT user_id FROM posts WHERE id=%s", (i,)).fetchone()
            if existing and existing["user_id"] != author_id:
                raise ValueError(f"seed post ID {i} is already used by another author")
            conn.execute(
                """INSERT INTO posts(id,user_id,content,like_count,created_at,modified_at)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (i, author_id, body, (i * 17) % 101, post_created_at(i, now), now),
            )
        # Explicit seed IDs must not collide with the app's next generated ID.
        for table in ("users", "posts"):
            conn.execute(f"""SELECT setval(pg_get_serial_sequence('{table}', 'id'),
                GREATEST((SELECT max(id) FROM {table}),
                         nextval(pg_get_serial_sequence('{table}', 'id'))), true)""")
    return {"users": 3, "posts": 200, "data": "synthetic", "reference_time": now.isoformat()}
