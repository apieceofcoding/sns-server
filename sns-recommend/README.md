# 추천 API와 worker

FastAPI는 저장된 추천 목록을 읽고, LangGraph worker는 목록을 미리 생성합니다. 조회와 스크롤에서는 모델을 호출하지 않아요.

## 실행

아래는 `main`의 전체 실행입니다. 1단원 시작은 [저장소 안내](../README.md)를 따릅니다. Docker와 uv를 준비하고 `sns-recommend/`에서 실행해요.

```sh
git switch main
uv sync --locked
docker compose up -d --wait
uv run sns-recommend seed
uv run sns-recommend index
uv run sns-recommend graph --user 1
docker compose --profile app up -d --build --wait

curl -H 'X-Internal-Token: course-local-token' http://localhost:8001/internal/feeds/1
```

API는 8001, PostgreSQL은 55432, Redis는 56379 포트입니다. `seed`가 테이블도 준비해요. 종료는 `docker compose --profile app down`입니다.

## 데이터

사용자 3명과 5개 주제의 글 200개를 만듭니다. [본문 예시](src/sns_recommend/post_examples.py)는 소재 10개 × 표현 4종으로 구성해요. 기존 ID는 건너뛰므로 새 예시는 빈 실습 DB에서 확인합니다.

T는 seed 응답의 `reference_time`입니다.

| 글 ID | 작성 시각 | T 기준 시간 필터 |
|---|---|---|
| 1~5 | 48시간 1분 전 | 제외 |
| 6~10 | 정확히 48시간 전 | 포함 |
| 11~15 | 47시간 59분 전 | 포함 |
| 16~20 | 1분 뒤 | 제외 |
| 21~200 | 최근 1~180분 | 포함 |

경계 검사는 `retrieve_candidates(user_id, as_of=T)`로 시각을 고정합니다. 시간 조건을 통과하는 190개에 다른 필터와 후보 제한을 추가해요. SNS 원본 데이터는 별도 연결해야 합니다.

## 모델 설정

`.env.example`을 `.env`로 복사해 설정합니다.

| MODEL_MODE | 동작 |
|---|---|
| fixture | 기본값. 합성 벡터와 순위, 외부 호출 없음 |
| live | 개인 키로 실제 API 호출 |
| record | 실제 호출과 응답 저장 |
| replay | 동일 입력과 모델의 저장된 응답 재생 |

`GOOGLE_API_KEY`는 worker에만 전달합니다. 일일 외부 호출 예산은 기본 20회이며 제공자의 무료 한도와 다릅니다. 실제 품질과 무료 한도는 별도 확인해요. 녹화 파일은 Git에 넣지 않습니다.

live/record 색인은 호출당 최대 20개 글을 처리하므로 남은 글이 있으면 `index`를 반복합니다. 동일 입력은 캐시를 사용해요.

## 검증

```sh
uv run sns-recommend evaluate
uv run sns-recommend benchmark
uv run python -m pytest -q
RUN_INTEGRATION=1 uv run python -m pytest -q
```

`evaluate`는 합성 정답셋 평가, `benchmark`는 Redis 조회 측정입니다. 실제 클릭률과 SNS 전체 응답 시간을 나타내지는 않아요. 통합 검사는 별도 테스트 DB와 Redis 15번 DB를 사용하므로 실습 전용 저장소를 지정합니다.

복구 실습은 Compose worker를 멈춘 뒤 실행해요.

```sh
docker compose --profile app stop worker
uv run sns-recommend graph --user 1 --pause-after-rerank
uv run python -m sns_recommend.worker --once
docker compose --profile app start worker
```

모델 결과 저장 후에는 재개할 수 있지만 저장 전 중단은 재호출될 수 있습니다.

## 코드 찾기

| 위치 | 역할 |
|---|---|
| `api/`, `cli.py` | HTTP와 실습 명령 |
| `data/`, `storage/` | 데이터 반영, DB, 목록과 작업 저장 |
| `providers/`, `recommenders/` | 모델 호출, 검색과 순위 규칙 |
| `pipelines/`, `worker/` | 생성, 예약과 복구 |
| `core/`, `evaluation/` | 설정, 사용량과 평가 |

최종 코드는 `src/sns_recommend/` 기준입니다. 이전 챕터의 파일 배치는 다를 수 있어요. 입력 규격은 실행 중인 API의 `/docs`, SNS 연결은 [연동 예제](integrations/sns-app/README.md)를 확인합니다.
