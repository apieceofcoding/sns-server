# SNS 추천 실습

**part-1부터 part-9까지 순서대로 진행합니다.** 기본 모델은 모의 응답이라 API 키와 호출 비용이 필요 없어요.

[SNS 화면](sns-front/README.md) | [Spring API](sns-app/README.md) | [Python 추천 서비스](sns-recommend/README.md)

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

최신순 추천을 Redis에 저장합니다. `baseline`은 저장을 마치면 종료해요.

```sh
git switch part-2-feed-api
uv sync --locked
docker compose -f ../sns-app/docker-compose.yml up -d --wait postgres
docker compose up -d --wait
uv run sns-recommend baseline --user 7 --strategy latest
```

별도 터미널을 `sns-recommend/`에 열고 추천 API를 실행합니다. API는 계속 켜 두고 저장된 추천을 조회해요.

```sh
uv run uvicorn sns_recommend.api:app --port 8001
```

실습 터미널에서 추천 ID를 확인합니다. Windows에서는 `curl.exe`를 사용해요.

```sh
curl -fsS -H "X-Internal-Token: course-local-token" http://localhost:8001/internal/feeds/7
```

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

```sh
git switch part-9-resilience
uv sync --locked
uv run sns-recommend init
uv run sns-recommend graph --user 7
uv run sns-recommend benchmark --user 7
```

`reports/benchmark.json`에서 Redis 조회 속도와 목록 나이를 확인해요.

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

## 추가 실습

- [실제 Gemini 호출](sns-recommend/README.md#모델-설정)
- [SNS 앱 연결](sns-app/README.md#추천-연결)
