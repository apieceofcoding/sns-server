# SNS 추천 실습

기존 [SNS 앱](sns-app/README.md)에 [Python 추천 서비스](sns-recommend/README.md)를 추가합니다. **1~9단원을 순서대로 실행해요.** 기본 모델은 모의 응답을 사용하므로 API 키와 호출 비용이 필요 없습니다.

<details>
<summary>처음 한 번: 도구 설치 (Windows / macOS)</summary>

[Git](https://git-scm.com/downloads)도 준비합니다. `git --version`으로 설치를 확인해요.

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
uv python install 3.13
```

Java와 javac는 25, Docker는 서버 정보가 나와야 합니다. 다른 Java가 선택되면 `JAVA_HOME`과 PATH를 JDK 25로 맞춰 주세요. Gradle은 별도 설치하지 않으며, Windows에서는 `./gradlew` 대신 `.\gradlew.bat`를 사용합니다.

</details>

## 시작하기

Docker Desktop을 실행하고 저장소를 받습니다.

```sh
git clone https://github.com/apieceofcoding/sns-server.git
cd sns-server/sns-recommend
```

## 실습 순서

모든 명령은 `sns-recommend/`에서 실행합니다.

### part-1. 데이터 준비

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

### part-2. 추천 조회

```sh
git switch part-2-feed-api
uv sync --locked
docker compose up -d --wait
uv run sns-recommend baseline --user 1 --strategy latest
```

별도 터미널을 `sns-recommend/`에 열고 API를 실행해요.

```sh
uv run uvicorn sns_recommend.api:app --port 8001
```

실습 터미널에서 추천 ID를 확인합니다. Windows에서는 `curl.exe`를 사용해요.

```sh
curl -fsS -H "X-Internal-Token: course-local-token" http://localhost:8001/internal/feeds/1
```

### part-3. 이벤트 전달

```sh
git switch part-3-events
uv sync --locked
uv run sns-recommend init
uv run sns-recommend source-post --post 1001
```

2단원과 같은 명령으로 API를 다시 실행한 뒤 전송합니다.

```sh
uv run sns-recommend relay
```

`delivered: 1`을 확인해요. 이후 `init`은 필요한 DB 구조만 추가하며 데이터를 다시 만들지 않습니다.

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
uv run sns-recommend embedding --user 1
```

관심사에 맞는 추천 ID를 확인합니다.

### part-6. 재정렬

```sh
git switch part-6-reranking
uv sync --locked
uv run sns-recommend generate --user 1
```

재정렬한 추천 ID를 확인해요. 기본값은 모의 응답입니다.

### part-7. LangGraph

```sh
git switch part-7-langgraph
uv sync --locked
uv run sns-recommend graph --user 1
```

검색부터 추천 저장까지 실행합니다. 체크포인트 테이블은 자동으로 준비해요.

### part-8. 품질 평가

```sh
git switch part-8-evaluation
uv sync --locked
uv run sns-recommend evaluate
```

`reports/evaluation.json`에서 합성 데이터의 전략별 점수를 비교합니다.

### part-9. 조회 측정

```sh
git switch part-9-resilience
uv sync --locked
uv run sns-recommend init
uv run sns-recommend graph --user 1
uv run sns-recommend benchmark --user 1
```

`reports/benchmark.json`에서 Redis 조회 속도와 목록 나이를 확인해요.

## 종료

API와 worker를 `Ctrl+C`로 종료한 뒤 실행합니다. 데이터는 남아요.

```sh
# 2단원부터 실행
docker compose down
# SNS 앱 DB 종료
docker compose -f ../sns-app/docker-compose.yml stop postgres
```

다음에 이어 할 때는 해당 단원에서 `uv sync --locked`와 1단원의 SNS 앱 DB 실행 명령을 실행합니다. 2단원부터는 `docker compose up -d --wait`도 실행해요. `seed`는 반복하지 않아요.

## 추가 실습

- [이벤트, 복구, 자동 갱신과 검사](docs/practice.md)
- [실제 Gemini 호출](sns-recommend/README.md#모델-설정)
- [SNS 앱 연결](sns-app/README.md#추천-연결)
- [데이터 초기화](docs/practice.md#검사와-종료): 글 작성 후 48시간이 지나 추천 대상이 줄었을 때 확인해요.
