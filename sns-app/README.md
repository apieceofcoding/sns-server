# SNS 앱

Java 25와 Spring Boot로 로그인, 게시글과 타임라인을 제공합니다. Git 브랜치는 [상위 저장소](../README.md)에서 함께 관리해요.

## 실행

JDK 25와 Docker를 준비하고 `sns-app/`에서 실행합니다.

```sh
./gradlew jibDockerBuild
docker compose up -d
curl -fsS http://localhost:8080/actuator/health
```

| 서비스 | 로컬 포트 |
|---|---|
| 앱 | 8080 |
| PostgreSQL / Redis | 5432 / 6379 |
| RustFS | 9000 / 9001 |

종료는 `docker compose down`입니다.

## 추천 연결

`GET /api/v1/recommendations`가 FastAPI를 호출합니다. 로그인한 사용자 ID로 추천을 읽고, 삭제된 글을 제외한 뒤 추천 순서대로 게시글을 응답해요.

| 설정 | 기본값 |
|---|---|
| `RECOMMENDATION_BASE_URL` | 로컬 `http://localhost:8001`, Docker `http://host.docker.internal:8001` |
| `INTERNAL_TOKEN` | `course-local-token`, 추천 API와 동일하게 설정 |

추천 API는 Docker에서 접근할 수 있도록 `--host 0.0.0.0`으로 실행합니다. 기존 `/v1/rank` 클라이언트는 이전 강의의 관측 데모 전용이에요.

### 조회 확인

가입한 계정으로 로그인하고 사용자 ID를 확인합니다. 아래 계정 정보를 본인 계정으로 바꿔요. Windows에서는 `curl.exe`를 사용합니다.

```sh
curl -fsS -c cookies.txt -X POST http://localhost:8080/api/v1/login -d "username=your-username&password=your-password"
curl -fsS -b cookies.txt http://localhost:8080/api/v1/users/me
```

`sns-recommend/`에서 응답의 `id`를 `--user`에 넣어 추천을 생성해요.

```sh
uv run sns-recommend baseline --user 10 --strategy latest
```

위 `10`은 본인 ID로 바꿉니다. 로그인했던 터미널에서 SNS API를 조회해요.

```sh
curl -fsS -b cookies.txt http://localhost:8080/api/v1/recommendations
```

`mode: recommend`와 `posts`를 확인합니다. 다음 페이지는 응답의 `nextCursor`를 `cursor` 쿼리에 넣어요.

| 상황 | 응답 |
|---|---|
| 추천 준비 전 또는 첫 조회 연결 실패 | `mode: latest`, 최신순으로 대체 |
| 최신순 다음 페이지 | `latest:` 커서로 최신순 유지 |
| 추천 커서 변조 또는 사용자 불일치 | 400 |
| 추천 커서 만료 | 410, 커서 없이 새 조회 |
| 추천 다음 페이지 연결 실패 | 503, 동일 커서로 재시도 |

게시글 이벤트 전달은 [연동 예제](../sns-recommend/integrations/sns-app/README.md)를 참고해요.
