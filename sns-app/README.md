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

현재 `/v1/rank`는 이전 강의의 mock 연동입니다. [Spring 연결 예제](https://github.com/apieceofcoding/sns-service/blob/main/sns-recommend/integrations/sns-app/README.md)를 적용해 FastAPI의 추천 ID를 원본 게시글로 바꿔 응답해요. 예제는 후반 챕터와 `main`에 있습니다.

기존 클라이언트와 예제의 `RecommendClient`는 빈 이름이 같으므로 기존 코드를 정리한 뒤 적용합니다.
