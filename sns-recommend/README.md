# SNS 추천 서비스

Python과 FastAPI로 추천을 생성하고 조회합니다. 생성 작업은 결과를 Redis에 저장하고, API는 저장된 목록을 읽어요.

**part-1부터 part-9까지 순서대로 진행합니다.** 기본 모델은 모의 응답이라 API 키와 호출 비용이 필요 없어요.

[실습 순서](#실습-순서) | [실습 데이터](#실습-데이터) | [저장 위치](#저장-위치) | [모델 설정](#모델-설정)

<details>
<summary>처음 한 번: 도구 설치 (Windows / macOS)</summary>

[Node.js LTS](https://nodejs.org/)와 [Git](https://git-scm.com/downloads)을 준비합니다. `git --version`으로 설치를 확인해요.

### Windows (PowerShell)

[Java 25 설치](https://adoptium.net/installation/)와 [uv 설치](https://docs.astral.sh/uv/getting-started/installation/) 명령입니다.

```powershell
winget install --exact --id EclipseAdoptium.Temurin.25.JDK
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)을 설치하고 실행합니다. WSL 2가 없다면 관리자 PowerShell에서 `wsl --install` 후 재부팅해요. Docker는 WSL 2 기반 Linux 컨테이너를 사용합니다. 실습 명령은 Windows PowerShell에서 실행하세요.

### macOS (터미널)

[Homebrew](https://brew.sh)가 없다면 먼저 설치합니다. 다음으로 [Java 25](https://formulae.brew.sh/cask/temurin@25)와 [uv](https://docs.astral.sh/uv/getting-started/installation/)를 설치해요.

```sh
brew install --cask temurin@25
brew install uv
```

[Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)에서 Apple Silicon 또는 Intel에 맞는 파일을 받아 설치하고 실행합니다.

### 설치 확인 (공통)

터미널을 다시 열고 Docker Desktop이 실행된 상태에서 확인해요.

```sh
java -version
javac -version
docker info
docker compose version
uv --version
node --version
npm --version
uv python install 3.13
```

Java와 javac는 25, Docker는 서버 정보가 나와야 합니다. 다른 Java가 선택되면 `JAVA_HOME`과 PATH를 JDK 25로 맞춰 주세요. Gradle은 별도 설치하지 않으며, Windows에서는 `./gradlew` 대신 `.\gradlew.bat`를 사용합니다.

</details>

## 시작하기

Docker Desktop을 실행하고 저장소를 받습니다.

```sh
git clone https://github.com/apieceofcoding/sns-service.git
cd sns-service/sns-recommend
```

## 실습 순서

실습 터미널은 `sns-recommend/`를 기준으로 사용합니다. 브랜치를 바꾸기 전 추천 API와 worker를 `Ctrl+C`로 종료해요.

### part-1. SNS 실행과 데이터 관찰

SNS 앱을 빌드하고 실행합니다. Windows에서는 `./gradlew` 대신 `.\gradlew.bat`를 사용해요.

```sh
git switch part-1-environment
cd ../sns-app
./gradlew jibDockerBuild
docker compose up -d --wait
```

[상태 확인](http://localhost:8080/actuator/health)에서 `UP`을 확인하고 실습 데이터를 만듭니다.

```sh
cd ../sns-recommend
uv sync --locked
uv run sns-recommend seed
docker compose -f ../sns-app/docker-compose.yml exec postgres psql -U snsuser -d snsdb -P pager=off
```

회원과 게시글을 조회하고 `\q`로 DB 접속을 종료해요.

```sql
SELECT id, username, created_at FROM users ORDER BY id;
SELECT id, user_id, left(content, 60) AS content, created_at FROM posts ORDER BY id LIMIT 5;
\q
```

별도 터미널을 `sns-service/`에 열어 화면을 실행합니다.

```sh
cd sns-front
npm ci
npm run dev
```

[SNS 화면](http://localhost:3000)에서 새 계정으로 가입해 로그인과 글 작성을 확인해요. 실습 계정에는 비밀번호가 없으며, 추천 비교에는 독자 7~9번을 사용합니다.

### part-2. 추천 생성과 조회

연동 코드가 포함된 SNS 앱을 다시 빌드하고 최신순 추천을 저장합니다. `baseline`은 저장을 마치면 종료해요.

```sh
git switch part-2-feed-api
cd ../sns-app
./gradlew jibDockerBuild
docker compose up -d --wait
cd ../sns-recommend
uv sync --locked
docker compose up -d --wait
uv run sns-recommend baseline --user 7 --strategy latest
```

별도 터미널을 `sns-recommend/`에 열고 추천 API를 실행합니다. API는 계속 켜 두고 저장된 추천을 조회해요.

```sh
uv run uvicorn sns_recommend.api:app --host 0.0.0.0 --port 8001
```

실습 터미널에서 추천 ID를 확인합니다. Windows에서는 `curl.exe`를 사용해요.

```sh
curl -fsS http://localhost:8001/internal/feeds/7
```

[SNS 앱 조회 확인](../sns-app/README.md#조회-확인)의 가입, 로그인, 추천 생성과 조회를 진행해요. 로그인한 계정의 ID로 추천을 생성하면 SNS가 추천 ID를 게시글로 바꿔 응답합니다.

### part-3. 이벤트 전달

```sh
git switch part-3-events
uv sync --locked
docker compose up -d --wait
uv run sns-recommend init
uv run sns-recommend source-post --post 1001
```

2단원과 같은 명령으로 API를 다시 실행한 뒤 전송합니다.

```sh
uv run sns-recommend relay
```

`delivered: 1`을 확인해요. `init`은 필요한 DB 구조를 추가하고 기존 데이터를 유지합니다.

### part-4. 게시글 색인

```sh
git switch part-4-indexing
uv sync --locked
uv run sns-recommend init
uv run sns-recommend index
```

게시글 벡터를 저장합니다. 다시 실행하면 `indexed: 0`이에요.

### part-5. 관심사 검색

```sh
git switch part-5-retrieval
uv sync --locked
uv run sns-recommend init
uv run sns-recommend embedding --user 7
```

관심사에 맞는 추천 ID를 확인합니다.

### part-6. 재정렬

```sh
git switch part-6-reranking
uv sync --locked
uv run sns-recommend generate --user 7
```

재정렬한 추천 ID를 확인해요.

### part-7. LangGraph

```sh
git switch part-7-langgraph
uv sync --locked
uv run sns-recommend graph --user 7
```

검색부터 추천 저장까지 실행합니다. 체크포인트 테이블은 자동으로 준비해요.

### part-8. 품질 평가

```sh
git switch part-8-evaluation
uv sync --locked
uv run sns-recommend evaluate
```

`reports/evaluation.json`에서 합성 데이터의 전략별 점수를 비교합니다.

### part-9. 조회 측정과 자동 갱신

최신순 대체와 자동 갱신을 확인합니다. SNS 앱을 다시 빌드해요.

```sh
git switch part-9-resilience
cd ../sns-app
./gradlew jibDockerBuild
docker compose up -d --wait
cd ../sns-recommend
uv sync --locked
uv run sns-recommend init
uv run sns-recommend graph --user 7
uv run sns-recommend benchmark --user 7
```

`reports/benchmark.json`에서 Redis 조회 속도와 목록 나이를 확인해요. 추천 API를 중단하고 SNS 추천 피드를 새로 조회하면 `mode: latest`로 응답합니다. 이 목록의 다음 페이지는 `latest:` 커서를 사용해요.

2단원 명령으로 추천 API를 다시 실행하고 피드를 조회합니다. 별도 터미널의 `sns-recommend/`에서 worker를 켜요.

```sh
uv run python -m sns_recommend.worker
```

worker는 계속 실행하며 약 30초마다 갱신 대상을 점검해요. 최근 30분 안에 추천 피드를 조회했고 최근 5분 안에 생성 작업이 없는 사용자를 예약하고 처리합니다.

## 종료

화면 서버, 추천 API와 worker를 `Ctrl+C`로 종료합니다. 아래 명령으로 SNS 앱과 추천 저장소를 종료해요. 두 번째 명령은 part-2부터 사용하며 데이터는 유지됩니다.

```sh
docker compose -f ../sns-app/docker-compose.yml down
docker compose down
```

<details>
<summary>다음에 이어서 실행하기</summary>

해당 브랜치의 `sns-recommend/`에서 실행해요.

```sh
uv sync --locked
docker compose -f ../sns-app/docker-compose.yml up -d --wait
```

part-2부터는 추천 저장소도 시작합니다.

```sh
docker compose up -d --wait
```

화면, 추천 API와 worker는 필요한 단원의 명령으로 다시 실행해요.

</details>

## 실습 데이터

작성자 6명, 독자 3명과 게시글 240개를 준비합니다.

| ID | 역할 | 주제 또는 관심사 |
|---|---|---|
| 1 | 작성자 | 백엔드 개발 |
| 2 | 작성자 | 여행 |
| 3 | 작성자 | 운동 |
| 4 | 작성자 | AI 개발 |
| 5 | 작성자 | 여행 유튜브 |
| 6 | 작성자 | 운동 식단 |
| 7 | 독자 | 백엔드와 AI 개발 |
| 8 | 독자 | 여행과 여행 유튜브 |
| 9 | 독자 | 운동과 운동 식단 |

작성자는 자기 주제만 40개씩 쓰고 독자는 글을 쓰지 않아요. 본문은 주제별 소재 10개와 표현 4종으로 만듭니다. 추천 프로필은 같은 사용자 ID를 사용합니다.

생성 시각 T를 기준으로 글 ID 1~6은 48시간 1분 전, 7~12는 정확히 48시간 전, 13~18은 47시간 59분 전, 19~24는 1분 뒤입니다. 25~240은 최근 1~216분이에요. 각 시간 경계에 모든 주제가 하나씩 있으며 T 기준 추천 가능한 글은 228개입니다.

`seed`는 1단원에서 한 번 실행합니다. 이전 구성과 ID가 충돌하면 중단하므로 빈 실습 DB에서 시작해요. 기존 DB를 자동 삭제하거나 덮어쓰지 않습니다.

## 저장 위치

| 저장소 | 내용 | 연결 설정 |
|---|---|---|
| SNS DB (`snsdb`, 5432) | 회원과 게시글 원본, 관심사, Outbox | `SOURCE_DATABASE_URL` |
| 추천 DB (`recommend`, 55432) | 글 ID별 벡터, 행동, 작업과 체크포인트 | `DATABASE_URL` |
| Redis (56379) | 완성된 추천 ID 목록 | `REDIS_URL` |

게시글과 회원은 복사하지 않습니다. 추천 DB는 글 ID, 버전과 벡터만 저장하고, 본문과 작성 시각은 검색할 때 SNS DB에서 읽어요. 글이 바뀌면 SNS가 글 ID와 버전만 이벤트로 알리고, worker가 원본을 다시 읽어 벡터를 갱신합니다.

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
