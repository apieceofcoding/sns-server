# 2. 저장된 추천 피드 조회

1단계 환경을 이어받습니다. API는 Redis 목록만 읽고 모델을 호출하지 않아요.

```sh
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend seed
uv run sns-recommend baseline --strategy latest
uv run uvicorn sns_recommend.api:app --port 8001
```

다른 터미널에서 조회합니다.

```sh
curl -H 'X-Internal-Token: course-local-token' http://localhost:8001/internal/feeds/1
uv run pytest
```

다음 페이지는 `next_cursor`를 그대로 전달해요. 첫 페이지에 목록이 없으면 `ready: false`, 만료된 커서는 410을 반환합니다. 원본 검사는 SNS에서 수행합니다.
