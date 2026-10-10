# SNS 추천 서비스

2단원 코드입니다. [저장소 안내](../README.md)의 순서로 진행해요.

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

이 단원부터 Redis를 사용합니다. 위의 Compose 명령으로 실행하고, 아래 명령으로 추천 ID 목록을 저장해요. 전체 명령은 `uv run sns-recommend --help`로 확인해요.

```sh
uv run sns-recommend baseline --user 1 --strategy latest
```

API는 `uv run uvicorn sns_recommend.api:app --port 8001`로 실행합니다. `/internal/feeds/1` 조회에는 `X-Internal-Token: course-local-token` 헤더를 사용해요.

## 검사와 종료

`uv run python -m pytest -q`로 검사하고 `docker compose down`으로 종료합니다. 통합 검사를 실행한다면 실습 전용 DB와 Redis를 사용해요.
