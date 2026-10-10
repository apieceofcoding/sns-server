# 상세 실습

[기본 순서로 돌아가기](../README.md#실습-순서)

추가 비교, 이벤트 전송과 복구를 직접 확인할 때 사용합니다. 명령은 `sns-recommend/`에서 실행해요.


처음에는 저장소를 받고 `sns-recommend/`로 이동합니다. 이미 받았다면 `cd sns-server/sns-recommend`부터 시작해요.

```sh
git clone https://github.com/apieceofcoding/sns-server.git
cd sns-server/sns-recommend
```

아래 명령은 모두 **`sns-recommend/`에서 1~9단원 순서로** 실행합니다. 브랜치를 바꾸기 전 API와 worker를 `Ctrl+C`로 종료해요. DB와 Redis의 데이터는 다음 단원에서도 유지합니다.

`seed`는 1단원에서 테이블과 데이터를 한 번 준비합니다. 3, 4, 5, 9단원에서는 `init`으로 DB 구조만 갱신해요. 기존 데이터는 유지합니다. 기본 모델은 `fixture`라 외부 API 비용이 없습니다.

### 1. 환경과 데이터

```sh
git switch part-1-environment
uv sync --locked
docker compose -f ../sns-app/docker-compose.yml up -d --wait postgres
uv run sns-recommend seed
```

DB에 접속합니다.

```sh
docker compose -f ../sns-app/docker-compose.yml exec postgres psql -U snsuser -d snsdb -P pager=off
```

사용자와 게시글 샘플을 조회해요.

```sql
SELECT id, username, created_at
FROM users
ORDER BY id
LIMIT 5;

SELECT id, user_id, left(content, 60) AS content, created_at
FROM posts
ORDER BY id
LIMIT 5;
```

`\q`를 입력해 DB 접속을 종료합니다.



### 2. 저장된 추천 조회

```sh
git switch part-2-feed-api
uv sync --locked
docker compose up -d --wait
uv run sns-recommend baseline --user 1 --strategy latest
```

이 단원부터 Redis에 추천 ID를 저장합니다. 아래 공통 API 실행과 조회로 `ready: true`를 확인한 뒤, `uv run sns-recommend baseline --user 1 --strategy popular`로 인기순도 비교해요.

**API 실행과 조회 (2단원부터 공통)**

단원 준비를 마친 뒤, 별도 터미널을 `sns-recommend/`에 열어 실행합니다.

```sh
uv run uvicorn sns_recommend.api:app --port 8001
```

실습 터미널에서 조회해요. Windows PowerShell에서는 `curl`을 `curl.exe`로 바꿉니다.

```sh
curl -fsS -H "X-Internal-Token: course-local-token" http://localhost:8001/internal/feeds/1
```

응답의 `post_ids`가 추천 순서입니다. `next_cursor`가 있으면 같은 주소에 `?cursor=값`을 붙여 다음 페이지를 조회해요.

### 3. Outbox 전달

```sh
git switch part-3-events
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend source-post --post 1001 --body "Python PostgreSQL 백엔드 실습"
```

공통 명령으로 API를 다시 실행한 뒤 전송합니다.

```sh
uv run sns-recommend relay
uv run sns-recommend relay
uv run sns-recommend status
```

처음에는 `delivered: 1`, 두 번째는 `delivered: 0`입니다. 새 글까지 포함해 게시글은 201개예요. 현재 명령은 Python의 `source_demo`를 사용하며 Spring Outbox와 별도입니다.

좋아요 행동도 API로 전달합니다. 응답에서 `accepted: true`를 확인해요.

```sh
uv run python -c "
import uuid, httpx
response = httpx.post(
    'http://localhost:8001/internal/events',
    headers={'X-Internal-Token': 'course-local-token'},
    json=dict(event_id=str(uuid.uuid4()), kind='like', user_id=1, post_id=1001),
)
response.raise_for_status()
print(response.json())
"
```

### 4. 게시글 색인

```sh
git switch part-4-indexing
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend index
uv run sns-recommend index
```

첫 실행은 벡터를 저장하고 두 번째는 `indexed: 0`입니다. 기본값은 모의 임베딩이에요.

### 5. 관심사 기반 후보

```sh
git switch part-5-retrieval
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend embedding --user 1
uv run sns-recommend embedding --user 2
```

관심사가 다른 사용자의 `post_ids`를 비교합니다. API를 실행하면 저장된 목록도 조회할 수 있어요.

### 6. 재정렬

```sh
git switch part-6-reranking
uv sync --locked
docker compose up -d --wait
uv run sns-recommend generate --user 1
```

후보 ID 검증과 다양성 조정을 거친 순위가 저장됩니다. 실제 Gemini 호출은 [모델 설정](../sns-recommend/README.md#모델-설정)을 따릅니다.

### 7. LangGraph와 복구

```sh
git switch part-7-langgraph
uv sync --locked
docker compose up -d --wait
uv run python -m sns_recommend.worker --once
uv run python -m sns_recommend.worker --once
uv run sns-recommend graph --user 1
uv run sns-recommend graph --user 1 --pause-after-rerank
uv run python -m sns_recommend.worker --once
```

앞의 두 worker 실행은 3단원에서 남은 색인과 관심사 갱신 작업을 처리합니다. `paused: true`로 중단한 뒤 마지막 명령으로 이어서 처리해요. 실습 중 다른 worker는 실행하지 않습니다.

### 8. 품질 평가

```sh
git switch part-8-evaluation
uv sync --locked
docker compose up -d --wait
uv run sns-recommend evaluate
```

`reports/evaluation.json`에서 전략별 Recall과 NDCG를 비교합니다. 고정된 합성 정답셋 평가이며, 실제 클릭률이나 Gemini 품질을 뜻하지 않아요.

### 9. 갱신과 조회 측정

```sh
git switch part-9-resilience
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend graph --user 1
uv run sns-recommend benchmark --user 1
uv run sns-recommend schedule
uv run python -m sns_recommend.worker --once
```

`reports/benchmark.json`에서 Redis 조회 p95와 목록 나이를 확인합니다. `schedule`은 최근 30분의 활성 사용자 중 갱신 대상만 예약하므로 `scheduled: 0`일 수도 있어요.

갱신을 계속 처리하려면 별도 터미널에서 실행합니다.

```sh
uv run python -m sns_recommend.worker
```

## 검사와 종료

각 단원에서 검사할 수 있습니다.

```sh
uv run python -m pytest -q
```

API와 worker를 `Ctrl+C`로 종료한 뒤 컨테이너를 내립니다. 데이터는 유지해요.

```sh
docker compose -f ../sns-app/docker-compose.yml stop postgres
# 2단원부터 실행
docker compose down
```

글 작성 시각은 다시 seed해도 바뀌지 않습니다. 48시간 뒤에는 추천 대상이 줄어들 수 있어요. **실습 데이터를 지우고 1단원부터 다시 시작할 때만** 다음 명령을 사용합니다.

```sh
docker compose down -v
```

## SNS 앱 연결

SNS 앱 실행은 [앱 안내](../sns-app/README.md), FastAPI 연결은 [Spring 연동 예제](https://github.com/apieceofcoding/sns-server/blob/main/sns-recommend/integrations/sns-app/README.md)를 따릅니다. 현재 앱의 추천 연결은 이전 mock이며 예제를 별도로 적용해야 해요.
