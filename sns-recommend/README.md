# SNS 추천 서비스

7단원 코드입니다. [저장소 안내](../README.md)의 순서로 진행해요.

## 시작하기

Docker와 uv를 준비하고 `sns-recommend/`에서 실행합니다.

```sh
uv sync --locked
docker compose up -d --wait
uv run sns-recommend seed
uv run sns-recommend status
```

`seed`가 테이블과 사용자 3명, 글 200개를 준비합니다. 추천 DB만 채우고 기존 ID는 덮어쓰지 않아요. DB는 55432, Redis는 56379 포트입니다.

## 데이터

5개 주제별 소재 10개와 표현 4종으로 글을 만듭니다. [본문과 작성 시각](src/sns_recommend/post_examples.py)을 수정할 수 있어요. 외부 API 호출은 없습니다.

seed의 `reference_time`을 T로 삼습니다. ID 1~5는 48시간 1분 전, 6~10은 정확히 48시간 전, 11~15는 47시간 59분 전, 16~20은 1분 뒤, 나머지는 최근 1~180분입니다. T 기준 시간 조건을 통과하는 글은 190개예요. 기존 데이터의 시각은 재실행으로 초기화하지 않습니다.

## 추천 실습

아래 순서로 실행합니다. 전체 명령은 `uv run sns-recommend --help`로 확인해요.

```sh
uv run sns-recommend baseline --user 1 --strategy latest
uv run sns-recommend index
uv run sns-recommend embedding --user 1
uv run sns-recommend generate --user 1
uv run sns-recommend graph --user 1
```

API는 `uv run uvicorn sns_recommend.api:app --port 8001`로 실행합니다. `/internal/feeds/1` 조회에는 `X-Internal-Token: course-local-token` 헤더를 사용해요.

기본 `fixture`는 모의 벡터와 순위입니다. `live`는 실제 API, `record`는 응답 저장, `replay`는 저장된 응답 재생이에요. 키와 모델은 `.env`에서 설정하고, 녹화 파일은 Git에 넣지 않습니다.

복구 실습은 다른 worker를 멈추고 `graph --user 1 --pause-after-rerank` 뒤 `uv run python -m sns_recommend.worker --once`를 실행해요. 저장 전 중단은 모델 재호출로 이어질 수 있습니다.

## 검사와 종료

`uv run python -m pytest -q`로 검사하고 `docker compose down`으로 종료합니다. 통합 검사를 실행한다면 실습 전용 DB와 Redis를 사용해요.
