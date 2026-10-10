# SNS 추천 서비스

1단원은 실습 데이터 준비까지만 진행합니다. FastAPI는 저장된 추천 목록을 읽고, worker는 목록을 미리 만듭니다.

**실행 명령은 [저장소 README](../README.md#실습-순서)에 1~9단원 순서로 모았습니다.** 준비, API 조회, 이벤트 전달, 복구와 종료를 그 순서대로 진행해요.

## 데이터와 포트

| 항목 | 내용 |
|---|---|
| 데이터 | 사용자 3명, 5개 주제의 글 200개. 3단원에서 글 1개 추가 |
| seed | 테이블 준비 후 기존 ID를 건너뜀. 본문과 시각을 덮어쓰지 않음 |
| 원본 PostgreSQL | 18, snsdb, 5432 |
| 벡터 PostgreSQL | 18 + pgvector, recommend, 55432 |
| Redis | 56379. 2단원부터 추천 ID 목록 저장 |
| FastAPI | 8001. 2단원부터 실행 |

원본 사용자와 게시글은 앱의 `snsdb`(5432)에 저장합니다. `SOURCE_DATABASE_URL`은 원본 DB, `DATABASE_URL`은 벡터 DB(55432) 연결이에요. `seed`와 `status`는 원본 DB를 사용하며, 추천 DB에 `users`, `posts`를 만들지 않습니다.

관심사 원문은 snsdb의 `user_interests`에 저장해요. 게시글은 앱의 `content`, `user_id`, `like_count` 컬럼을 사용합니다. seed 계정은 `course-user-1`부터 `course-user-3`까지이며 로그인용 비밀번호는 설정하지 않습니다.

두 DB는 PostgreSQL 18을 사용합니다. 추천 DB는 `recommend-index-pg18` 볼륨에서 새로 시작해요. 이전 실습 볼륨은 보존되지만 자동으로 이전되지 않습니다. 1단원은 pgvector 확장만 준비하고, 4단원부터 원본 ID와 임베딩, 검색용 메타데이터를 색인합니다.

[본문 예시](src/sns_recommend/post_examples.py)는 소재 10개와 표현 4종을 조합합니다. seed 응답의 `reference_time`을 T로 삼아요.

| 글 ID | 작성 시각 |
|---|---|
| 1~5 | T에서 48시간 1분 전 |
| 6~10 | T에서 정확히 48시간 전 |
| 11~15 | T에서 47시간 59분 전 |
| 16~20 | T에서 1분 뒤 |
| 21~200 | T에서 최근 1~180분 전 |

T 기준 시간 조건을 통과하는 글은 190개입니다. 실제 검색은 현재 시각을 쓰므로 시간이 지나면 결과가 달라져요. 추천 목록 조회의 Spring 연결은 [Spring 연동 예제](https://github.com/apieceofcoding/sns-server/blob/main/sns-recommend/integrations/sns-app/README.md)를 따릅니다.

## 모델 설정

4단원부터 적용합니다. `.env.example`을 `.env`로 복사하고 필요한 값을 입력해요.

| MODEL_MODE | 동작 |
|---|---|
| fixture | 기본값. 모의 벡터와 순위, 외부 호출 없음 |
| live | `GOOGLE_API_KEY`로 실제 Gemini 호출 |
| record | 실제 호출 후 응답 저장 |
| replay | 동일 입력과 모델의 저장된 응답 재생 |

실제 호출은 `EMBEDDING_MODEL`과 `RERANK_MODEL`도 설정합니다. live/record 색인은 한 번에 최대 20개 글을 처리하므로 남은 글이 있으면 `index`를 반복해요. 모델을 바꾸면 색인도 다시 실행합니다. API 키와 녹화 파일은 Git에 넣지 않습니다.

8단원 평가는 합성 정답셋, 9단원 benchmark는 Redis 읽기만 측정해요. 실제 클릭률과 SNS 전체 응답 시간을 뜻하지 않습니다. 기본 일일 호출 예산 20회는 제공자의 무료 한도와 다릅니다.

## DB 통합 테스트

두 DB를 실행한 뒤 macOS에서는 아래 명령으로 저장 위치와 seed 멱등성을 확인합니다. 빈 실습 DB를 기준으로 검사해요.

```sh
COURSE_DB_TESTS=1 uv run python -m pytest -q
```

Windows PowerShell에서는 먼저 `$env:COURSE_DB_TESTS="1"`을 설정하고 `uv run python -m pytest -q`를 실행합니다.
