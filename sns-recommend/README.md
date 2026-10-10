# SNS 추천 API와 worker

현재 코드는 모노레포의 `main`에 있습니다. Python API는 저장된 목록을 읽고, LangGraph worker는 외부 모델을 호출해 목록을 미리 만들어요.

## Python 패키지

`src/sns_recommend/` 아래를 역할별로 나눕니다. HTTP 라우터, 외부 모델 호출과 추천 규칙을 따로 읽을 수 있어요.

| 패키지 | 책임 |
|---|---|
| `api/` | FastAPI 앱, 내부 인증과 기능별 라우터 |
| `core/` | 설정, 리소스 경로와 호출 비용 기록 |
| `data/` | 이벤트 반영, 게시글 색인과 합성 데이터 준비 |
| `providers/` | 임베딩과 재정렬 API, fixture와 응답 재생 |
| `recommenders/` | 기본 추천, 후보 검색과 순위 검증, 다양성 규칙 |
| `pipelines/` | 함수 기반 생성과 LangGraph 실행, 복구와 발행 |
| `storage/` | PostgreSQL 연결, Redis 피드와 작업 저장 |
| `worker/` | 작업 실행 루프와 활성 사용자 갱신 예약 |
| `evaluation/` | 품질 지표, 오프라인 비교와 조회 측정 |

조회는 `api → data/storage`, 추천 생성은 `worker → pipelines → recommenders/providers`로 이어집니다. `recommenders/ranking.py`의 순위 검증과 다양성 규칙은 DB와 모델 API 없이 실행해요. `cli.py`는 실습 명령의 진입점입니다.

Python의 [src 레이아웃](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)과 FastAPI의 [APIRouter 분리](https://fastapi.tiangolo.com/tutorial/bigger-applications/)를 따릅니다. 이 원칙을 우리 서비스의 추천, 모델 호출과 실행 흐름에 맞춰 적용했어요.

패키지 분리는 최종 브랜치에 적용했습니다. 1~8장 브랜치는 이전 파일 배치로 단계별 구현을 보여줍니다. `uvicorn sns_recommend.api:app`, `python -m sns_recommend.worker`와 `sns-recommend` 명령은 동일해요.

## 처음 실행

```sh
git switch main
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend seed
uv run sns-recommend index
uv run sns-recommend graph --user 1
docker compose --profile app up -d --build --wait
```

```sh
curl -H 'X-Internal-Token: course-local-token' http://localhost:8001/internal/feeds/1
```

localhost의 8001은 추천 API, 55432는 추천 DB, 56379는 추천 Redis입니다. 기존 SNS와 별도 포트로 실행해요. `.env.example`을 `.env`로 복사해 설정을 바꿀 수 있습니다.

SQL과 고정 평가 데이터는 wheel에도 포함됩니다. 설치된 패키지에서는 `importlib.resources`로 읽고, 개발 환경에서는 저장소의 `sql/`과 `data/`를 사용해요.

## 모델 모드

| 모드 | 실행 |
|---|---|
| fixture (기본) | 합성 벡터와 순위. 실제 모델 출력 아님 |
| live | 개인 키로 Gemini 실제 호출 |
| record | 실제 호출과 응답 파일 저장 |
| replay | 같은 입력과 모델의 저장된 실제 응답 재생 |

실제 호출은 worker에만 GOOGLE_API_KEY를 전달합니다. API 컨테이너에는 키가 없어요. 실제 Gemini 품질과 계정별 무료 한도는 아직 검증하지 않았습니다. 모델 ID는 `.env.example`에서 변경할 수 있어요. record 파일은 Git에 넣지 않습니다.

live/record 색인은 20개 묶음부터 처리합니다. 변경 없는 본문은 캐시를 사용하며, fixture 벡터와 Gemini 벡터는 섞지 않아요. 재정렬 성공 경로는 일반 API 한 번 호출입니다. 일일 호출 예산은 모든 외부 모델 호출에 적용하고 20회부터 시작합니다. 이는 제공자의 실제 무료 한도와 별개입니다.

녹화 키에는 모델, 차원과 입력 묶음이 포함됩니다. record는 캐시를 포함한 전체 묶음을 저장하고, replay는 같은 묶음의 파일을 확인해요. 이전 형식의 임베딩 녹화 파일은 다시 생성해야 합니다. 파일은 작성자만 읽을 수 있는 권한으로 저장합니다.

## 내부 요청 규칙

| 입력 | 허용 범위 |
|---|---|
| 인증 토큰 | 공백 없는 ASCII 문자 1~512자. 빈 토큰 거부 |
| 게시글 | 본문 1~10,000자, 주제 1~100자, 양의 정수 작성자 ID |
| 관심사 | 문자열 1~1,000자 |
| 이벤트 | 양의 정수 ID와 버전, 시간대가 포함된 시각 |
| 피드 조회 | 1~50개, 서명된 커서 최대 512자 |

게시글 변경과 관심사 변경은 정해진 payload 필드만 받습니다. 삭제와 행동 이벤트의 payload는 비워요. 형식이나 길이가 맞지 않으면 DB와 모델 호출 전에 HTTP 422를 반환합니다.

## 복구와 평가

```sh
# Compose worker를 잠시 멈추고 재개 실습을 진행합니다.
docker compose --profile app stop worker
uv run sns-recommend graph --user 1 --pause-after-rerank
uv run python -m sns_recommend.worker --once
uv run sns-recommend evaluate
uv run sns-recommend benchmark
uv run pytest -q
RUN_INTEGRATION=1 uv run pytest -q
```

통합 검사는 별도 테스트 DB를 생성하고 실습 Redis의 15번 DB를 사용합니다. 기존 SNS의 DB나 Redis를 테스트 주소로 설정하지 않아요. evaluate는 고정 합성 데이터의 오프라인 평가입니다. benchmark는 Redis 조회만 측정하며 HTTP와 Spring 원본 조회를 포함하지 않습니다.

모델 결과 저장 후 중단되면 검증부터 이어갑니다. 저장 전 중단은 재호출될 수 있어요. 같은 스냅샷의 멱등 발행과 생성 세대 검사로 오래된 결과를 차단합니다. 현재 구현은 소규모 로컬 실습용이며 대규모 배포 구성은 후속 과정입니다.

작업은 최대 3회 시도합니다. 만료된 작업도 이 상한을 적용하고, 소유권을 잃은 worker는 체크포인트를 바꾸지 못해요. worker는 일시적인 DB 연결 오류 후 다시 시도하며 로그에는 오류 종류만 남깁니다.

후보 30개는 임베딩 20개에 최신 글과 인기 글을 각각 최대 5개 보충합니다. 중복으로 생긴 빈자리는 남은 후보로 채워요. 관심사에는 최근 7일 반응 중 가장 최근의 게시글 5개를 사용하고, 오래된 사용자 벡터는 유사도 계산에서 제외합니다.

## 이전 챕터 구성

| 브랜치 | 추가하는 것 |
|---|---|
| main | 시작 안내 |
| part-1 | uv, Compose와 합성 데이터 |
| part-2-feed-api | FastAPI, Redis 목록과 커서 |
| part-3-events | Outbox, 이벤트와 작업 |
| part-4-indexing | LangChain Document와 임베딩 |
| part-5-retrieval | 관심사 벡터와 후보 검색 |
| part-6-reranking | Gemini 재정렬과 출력 검증 |
| part-7-langgraph | 단계 상태, 분기와 복구 |
| part-8-evaluation | 네 전략의 시간 기준 평가 |
| part-9-resilience | 호출 예산, 갱신, 측정과 전체 검증 |

각 브랜치는 이전 챕터 커밋을 포함합니다. 브랜치를 바꾼 뒤 `uv sync --locked`와 `uv run sns-recommend init`을 실행해요. 완료된 스냅샷을 보존하며 다음 챕터를 이어갑니다.

[Spring SNS 연동 예제](integrations/sns-app/README.md)와 [코드 저장소 안내](../README.md)를 확인해요.

## 실습 게시글 예시

`uv run sns-recommend seed`는 주제별 세부 소재 10개와 표현 4종을 조합해, 5개 주제에 각각 40개의 서로 다른 글을 만듭니다. [post_examples.py](src/sns_recommend/post_examples.py)에서 소재와 표현을 바꿀 수 있어요. 외부 모델 호출은 없습니다.

기존 ID는 건너뛰므로 이미 만든 글을 덮어쓰지 않습니다. 새 예시는 빈 실습 DB에서 확인해요. 고정된 조합의 예시이며 실제 이용자 반응이나 추천 품질을 입증하는 데이터는 아닙니다.

### 48시간 경계 실습

seed 응답의 `reference_time`을 T로 사용합니다. ID 1~5는 T보다 48시간 1분 전, 6~10은 정확히 48시간 전, 11~15는 47시간 59분 전, 16~20은 1분 뒤입니다. 나머지 180개는 최근 1~180분에 배치해요. 각 경계 그룹에는 5개 주제가 하나씩 있습니다.

T에 고정한 시간 필터에서는 1~5와 16~20을 제외하고 190개가 대상입니다. 최종 후보 수는 다른 필터와 검색 제한에 따라 달라져요. 정확한 경계 검사는 `retrieve_candidates(user_id, as_of=T)`로 실행합니다. 실제 조회는 현재 시각을 쓰므로 시간이 흐르면 포함 여부가 변합니다. 기존 DB의 글은 덮어쓰지 않아요.
