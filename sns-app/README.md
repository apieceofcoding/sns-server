# SNS 추천 강의의 기반 앱

배포와 관측 강의의 완성된 SNS 앱에서 추천 기능 실습을 시작합니다. 이 폴더의 `main`에 변경을 쌓아가요.

| 항목 | 기준 |
|---|---|
| 가져온 코드 | `deploy-observability/sns-app`의 `part-9-ai-agent-analysis` |
| 기준 커밋 | `0efb6669480f1d37f99faf5621ec2415b3c75be5` |
| 실습 브랜치 | `main`만 유지 |
| 원격 저장소 | 연결하지 않음 |
| 추천 서비스 | 옆 폴더의 [sns-recommend](../sns-recommend/README.md) |

원본의 Git 이력을 보존하고 마지막 챕터를 `main`에 fast-forward로 합쳤습니다. 이전 강의의 브랜치 이름은 복사본에서 정리했어요.

## 로컬 실행

JDK 25와 Docker가 필요합니다. `sns-app/`에서 실행해요.

```sh
./gradlew jibDockerBuild
docker compose up -d
curl -fsS http://localhost:8080/actuator/health
```

앱은 8080, PostgreSQL은 5432, Redis는 6379, RustFS는 9000과 9001을 사용합니다. 종료할 때는 다음 명령을 실행해요.

```sh
docker compose down
```

## 여기서 이어갈 실습

기존 인증, 게시글과 타임라인에 추천 피드 조회와 행동 이벤트를 연결합니다. 추천 목록은 Python worker가 만들고, SNS 앱은 저장된 목록과 원본 게시글을 조회해요.

현재 포함된 `/v1/rank` 호출은 이전 강의의 mock 연동입니다. 새 추천 API에 맞춰 교체해야 해요. 기존 `domain.recommend.RecommendClient`와 연동 예제의 `RecommendClient`는 Spring 빈 이름이 같으므로, 예제를 그대로 추가하면 충돌합니다.


전체 실행 구조는 [코드 저장소 안내](../README.md)를 확인해요.
