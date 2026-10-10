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

Docker Desktop을 실행하고 저장소를 받습니다. 이미 받았다면 `sns-recommend/`로 이동해요.

```sh
git clone https://github.com/apieceofcoding/sns-server.git
cd sns-server/sns-recommend
```

## 실습 순서

**아래 표를 한 행씩 진행합니다.** 모든 명령은 `sns-recommend/`에서 실행해요.

1. 표의 브랜치로 이동: `git switch 브랜치명`
2. 아래 공통 준비 명령 실행
3. 표의 실습 명령 실행 후 결과 확인

```sh
uv sync --locked
docker compose -f ../sns-app/docker-compose.yml up -d --wait postgres
docker compose up -d --wait
```

`seed`는 snsdb에 앱 테이블과 사용자 3명, 게시글 200개를 준비합니다. 다른 계정이나 작성자가 같은 ID를 사용하면 중단해요. 원본 DB는 5432, 벡터 DB는 55432입니다. Redis는 2단원부터 실행됩니다.

**데이터는 1단원의 `seed`로 한 번만 만듭니다.** DB 구조가 추가되는 3, 4, 5, 9단원에서만 `init`을 실행해요. `init`은 기존 데이터를 유지하며 테이블과 컬럼을 준비합니다. 7단원 체크포인트 테이블은 LangGraph 실행 시 자동 생성됩니다.

| 단원 | 브랜치 | 실습 명령 | 확인 |
|---|---|---|---|
| 1. 데이터 | `part-1-environment` | `uv run sns-recommend seed`<br>`uv run sns-recommend status` | 사용자 3명, 글 200개 |
| 2. 추천 조회 | `part-2-feed-api` | `uv run sns-recommend baseline --user 1 --strategy latest` | 최신순 ID 목록 저장 |
| 3. 이벤트 전달 | `part-3-events` | `uv run sns-recommend init`<br>`uv run sns-recommend source-post --post 1001`<br>`uv run sns-recommend relay` | `delivered: 1` |
| 4. 색인 | `part-4-indexing` | `uv run sns-recommend init`<br>`uv run sns-recommend index` | 게시글 벡터 저장 |
| 5. 관심사 검색 | `part-5-retrieval` | `uv run sns-recommend init`<br>`uv run sns-recommend embedding --user 1` | 개인별 추천 ID |
| 6. 재정렬 | `part-6-reranking` | `uv run sns-recommend generate --user 1` | 재정렬한 추천 ID |
| 7. LangGraph | `part-7-langgraph` | `uv run sns-recommend graph --user 1` | 단계별 추천 생성 |
| 8. 품질 평가 | `part-8-evaluation` | `uv run sns-recommend evaluate` | reports/evaluation.json |
| 9. 조회 측정 | `part-9-resilience` | `uv run sns-recommend init`<br>`uv run sns-recommend benchmark --user 1` | reports/benchmark.json |

3단원은 실습 명령 전에 아래 방법으로 API를 실행합니다.

9단원에서 목록이 만료됐다면 `uv run sns-recommend graph --user 1`로 다시 만든 뒤 측정합니다. 8단원은 합성 데이터 평가, 9단원은 Redis 조회 측정이에요.

## API로 확인하기

2단원부터 사용할 수 있습니다. 별도 터미널을 `sns-recommend/`에 열어 실행해요.

```sh
uv run uvicorn sns_recommend.api:app --port 8001
```

실습 터미널에서 조회합니다. Windows에서는 `curl` 대신 `curl.exe`를 사용해요.

```sh
curl -fsS -H "X-Internal-Token: course-local-token" http://localhost:8001/internal/feeds/1
```

`ready: true`와 `post_ids`를 확인합니다. **다음 브랜치로 이동하기 전 API를 `Ctrl+C`로 종료하세요.**

## 더 실습하기

| 실습 | 안내 |
|---|---|
| 이벤트 전송과 좋아요 | [3단원](docs/practice.md#3-outbox-전달) |
| 중단 후 이어서 생성 | [7단원](docs/practice.md#7-langgraph와-복구) |
| 자동 갱신 | [9단원](docs/practice.md#9-갱신과-조회-측정) |
| 실제 Gemini 호출 | [모델 설정](sns-recommend/README.md#모델-설정) |
| SNS 화면 연결 | [앱 안내](sns-app/README.md#추천-연결) |

## 검사와 종료

검사는 `uv run python -m pytest -q`입니다. API와 worker를 `Ctrl+C`로 종료한 뒤 아래 명령을 실행해요. 데이터는 남습니다.

```sh
docker compose down
docker compose -f ../sns-app/docker-compose.yml stop postgres
```

48시간이 지나면 추천 대상 글이 줄어들 수 있습니다. 처음부터 다시 실습하려면 [데이터 초기화](docs/practice.md#검사와-종료)를 확인해요.
