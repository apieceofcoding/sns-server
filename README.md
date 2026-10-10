# SNS 추천 실습

Spring SNS와 Python 추천 서비스를 함께 관리하는 모노레포입니다. 서비스별로 빌드하고 HTTP로 연결해요.

| 서비스 | 역할 |
|---|---|
| [sns-app](sns-app/README.md) | 로그인, 게시글과 타임라인 |
| [sns-recommend](sns-recommend/README.md) | 추천 API와 목록을 미리 만드는 worker |

## 도구 설치

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

## 시작하기

Java 25, Docker와 uv를 준비합니다. 저장소 루트에서 실행해요.

```sh
git switch part-1-environment
cd sns-recommend
uv sync --locked
docker compose up -d --wait
uv run sns-recommend seed
uv run sns-recommend status
```

`seed`가 테이블과 실습 데이터를 준비합니다. 기존 ID는 덮어쓰지 않아요.
