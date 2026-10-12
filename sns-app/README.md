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
