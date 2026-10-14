# SNS 앱

Java 25와 Spring Boot로 로그인, 게시글과 피드 API를 제공합니다.

## 실행

JDK 25와 Docker를 준비하고 `sns-app/`에서 실행합니다.

```sh
./gradlew jibDockerBuild
docker compose up -d --wait
curl -fsS http://localhost:8080/actuator/health
```

종료는 `docker compose down`입니다.

## 추천 연결

`GET /api/v1/recommendations`가 FastAPI를 호출합니다. 로그인한 사용자 ID로 추천을 읽고, 삭제된 글을 제외한 뒤 추천 순서대로 게시글을 응답해요.

`RECOMMENDATION_BASE_URL`은 로컬에서 `http://localhost:8001`, Docker에서 `http://host.docker.internal:8001`입니다. 추천 API는 `--host 0.0.0.0`으로 실행해요.

### 조회 확인

추천 API를 켜 둔 상태에서 아래 명령은 모두 `sns-recommend/`의 같은 터미널에서 실행합니다. Windows에서는 `curl.exe`를 사용해요.

실습용 로그인 계정을 한 번 가입합니다. 이미 가입했다면 이 명령은 건너뛰어요.

```sh
curl -fsS -X POST http://localhost:8080/api/v1/users/signup -H "Content-Type: application/json" -d '{"username":"recommenddemo","password":"recommend1234"}'
```

같은 계정으로 로그인하고 사용자 ID를 확인합니다. `seed`로 만든 독자 7~9번은 비밀번호가 없어 로그인에 사용할 수 없어요.

```sh
curl -fsS -c cookies.txt -X POST http://localhost:8080/api/v1/login -d "username=recommenddemo&password=recommend1234"
curl -fsS -b cookies.txt http://localhost:8080/api/v1/users/me
```

응답의 `id`로 추천을 생성합니다. 아래 `10`은 예시이므로 확인한 ID로 바꿔요.

```sh
uv run sns-recommend baseline --user 10 --strategy latest
curl -fsS -b cookies.txt http://localhost:8080/api/v1/recommendations
```

`mode: recommend`와 `posts`를 확인합니다. 다음 페이지는 응답의 `nextCursor`를 `cursor` 쿼리에 넣어요.
