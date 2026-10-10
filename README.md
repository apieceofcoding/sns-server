# SNS AI 추천 실습 코드

기존 Spring SNS에 Python 추천 서비스를 연결하는 실습입니다. 이 폴더가 수강생에게 제공하는 Git 모노레포예요. 두 서비스는 함께 버전 관리하고 각각 빌드와 실행을 합니다.

| 폴더 | 역할 | 실행 안내 |
|---|---|---|
| sns-app | Java, Spring Boot SNS 앱 | [README](sns-app/README.md) |
| sns-recommend | Python, FastAPI 추천 API와 worker | [README](sns-recommend/README.md) |

## 시작하기

Java 25, Docker와 uv를 준비합니다. 먼저 각 서비스의 README에 따라 실행해요. 추천 API와 worker는 같은 Python 코드를 별도 프로세스로 실행합니다. 기본 fixture 모드는 외부 AI 비용 없이 합성 데이터로 흐름을 확인합니다.

```sh
cd sns-recommend
uv sync --locked
```

두 서비스 사이의 요청은 HTTP로 전달합니다. 한 저장소라고 Java와 Python의 의존성이나 실행 프로세스가 합쳐지는 것은 아니에요.

## Git 구성

`main`은 현재 완성 코드입니다. `part-1 → … → part-9-resilience` 순서로 챕터를 진행해요. 모든 챕터에는 `sns-app/`과 당시의 `sns-recommend/`가 함께 있습니다.

기존 추천 저장소의 커밋과 누적 관계를 보존했습니다. 파일을 `sns-recommend/` 아래로 옮겨 커밋 해시는 바뀌었지만 작성자, 메시지와 변경 이력은 남아 있어요. `sns-app/`은 모노레포 전환 시점의 코드로 고정되어 있으며 각 챕터에서 자동으로 연동이 완성되는 것은 아닙니다.

```sh
git switch part-1
# 다음 챕터
git switch part-2-feed-api
# 완성 코드
git switch main
```

기존 SNS의 mock 클라이언트를 새 추천 API와 연결하는 예제는 [Spring 연동 안내](sns-recommend/integrations/sns-app/README.md)에 있습니다. 초기 데이터의 사용자와 게시글 ID도 두 서비스에서 맞춰야 해요.

이 저장소에는 실습 소스와 실행 안내만 포함합니다. 강사용 도메인 문서, 슬라이드와 대본은 별도로 관리합니다.
