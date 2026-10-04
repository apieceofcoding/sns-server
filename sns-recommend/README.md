# SNS 추천 API와 worker

최종 코드는 `part-9-resilience`입니다. Python API는 저장된 목록을 읽고, LangGraph worker는 외부 모델을 호출해 목록을 미리 만들어요.

## 처음 실행

```sh
git switch part-9-resilience
uv sync --locked
docker compose up -d --wait
uv run sns-rec init
uv run sns-rec seed
uv run sns-rec index
uv run sns-rec graph --user 1
docker compose --profile app up -d --build --wait
```

```sh
curl -H 'X-Internal-Token: course-local-token' http://localhost:8001/internal/feeds/1
```

localhost의 8001은 추천 API, 55432는 추천 DB, 56379는 추천 Redis입니다. 기존 SNS와 별도 포트로 실행해요. `.env.example`을 `.env`로 복사해 설정을 바꿀 수 있습니다.

## 모델 모드

| 모드 | 실행 |
|---|---|
| fixture (기본) | 합성 벡터와 순위. 실제 모델 출력 아님 |
| live | 개인 키로 Gemini 실제 호출 |
| record | 실제 호출과 응답 파일 저장 |
| replay | 같은 입력과 모델의 저장된 실제 응답 재생 |

실제 호출은 worker에만 GOOGLE_API_KEY를 전달합니다. API 컨테이너에는 키가 없어요. 실제 Gemini 품질과 계정별 무료 한도는 아직 검증하지 않았습니다. 모델 ID는 `.env.example`에서 변경할 수 있어요. record 파일은 Git에 넣지 않습니다.

live/record 색인은 20개 묶음부터 처리합니다. 변경 없는 본문은 캐시를 사용하며, fixture 벡터와 Gemini 벡터는 섞지 않아요. 재정렬 성공 경로는 일반 API 한 번 호출입니다. 일일 호출 예산은 모든 외부 모델 호출에 적용하고 20회부터 시작합니다. 이는 제공자의 실제 무료 한도와 별개입니다.

## 복구와 평가

```sh
# Compose worker를 잠시 멈추고 재개 실습을 진행합니다.
docker compose --profile app stop worker
uv run sns-rec graph --user 1 --pause-after-rerank
uv run python -m sns_recommend.worker --once
uv run sns-rec evaluate
uv run sns-rec benchmark
uv run pytest -q
RUN_INTEGRATION=1 uv run pytest -q
```

통합 검사는 별도 테스트 DB를 생성하고 실습 Redis의 15번 DB를 사용합니다. 기존 SNS의 DB나 Redis를 테스트 주소로 설정하지 않아요. evaluate는 고정 합성 데이터의 오프라인 평가입니다. benchmark는 Redis 조회만 측정하며 HTTP와 Spring 원본 조회를 포함하지 않습니다.

모델 결과 저장 후 중단되면 검증부터 이어갑니다. 저장 전 중단은 재호출될 수 있어요. 같은 스냅샷의 멱등 발행과 생성 세대 검사로 오래된 결과를 차단합니다. 현재 구현은 소규모 로컬 실습용이며 대규모 배포 구성은 후속 과정입니다.

## 챕터 브랜치

| 브랜치 | 추가하는 것 |
|---|---|
| main | 시작 안내 |
| part-1-environment | uv, Compose와 합성 데이터 |
| part-2-feed-api | FastAPI, Redis 목록과 커서 |
| part-3-events | Outbox, 이벤트와 작업 |
| part-4-indexing | LangChain Document와 임베딩 |
| part-5-retrieval | 관심사 벡터와 후보 검색 |
| part-6-reranking | Gemini 재정렬과 출력 검증 |
| part-7-langgraph | 단계 상태, 분기와 복구 |
| part-8-evaluation | 네 전략의 시간 기준 평가 |
| part-9-resilience | 호출 예산, 갱신, 측정과 전체 검증 |

각 브랜치는 이전 챕터 커밋을 포함합니다. 브랜치를 바꾼 뒤 `uv sync --locked`와 `uv run sns-rec init`을 실행해요. 완료된 스냅샷을 보존하며 다음 챕터를 이어갑니다.

[챕터 자료](../materials/README.md), [Spring SNS 연동 예제](integrations/sns-app/README.md), [서비스 설계](../design/sns-recommend-service.md).
