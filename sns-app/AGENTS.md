# sns-app 작업 안내

게시글 작성과 타임라인 조회를 제공하는 Spring Boot SNS 앱입니다. 이전 강의의 `part-9-ai-agent-analysis`를 합친 `main`에서 추천 실습을 이어가요. 상위 코드 저장소의 [README.md](../README.md)를 함께 확인합니다.

- 요청한 범위의 코드만 변경해요. 파일 삭제는 사용자 확인을 받고, Git은 상태 확인에만 사용합니다. `git push`는 실행하지 않습니다.
- API 코드를 만들거나 수정할 때 [.agents/skills/spring-api-rules/SKILL.md](.agents/skills/spring-api-rules/SKILL.md)를 적용해요. 엔드포인트, record, FK, 트랜잭션과 API 실행 스크립트 규칙은 이 파일에서 관리합니다.
- `@RequestMapping`을 사용하지 않고 각 메서드에 전체 엔드포인트를 적습니다.
- JDK 25와 저장소의 Gradle wrapper를 사용합니다. Java 변경 후 `./gradlew spotlessApply`로 포맷을 맞추고 `./gradlew test`로 검증해요. `.claude`의 편집 후 훅은 Codex에서 실행되지 않으므로 명령을 직접 실행합니다.
- 장애 분석 실습의 관측 조회는 나란히 둔 `sns-devops`에서 진행해요. 그 저장소의 `skills/obsctl`과 `incident-analysis` 스킬을 사용합니다.
- 장애 조사 요청에서는 관측 근거와 대응안을 먼저 보고하고, 코드 수정이나 배포는 별도 요청 범위에 따라 수행해요.
