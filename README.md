# SNS 추천 실습

Spring SNS와 Python 추천 서비스를 함께 관리하는 모노레포입니다. 서비스별로 빌드하고 HTTP로 연결해요.

| 서비스 | 역할 |
|---|---|
| [sns-app](sns-app/README.md) | 로그인, 게시글과 타임라인 |
| [sns-recommend](sns-recommend/README.md) | 추천 API와 목록을 미리 만드는 worker |

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

## 브랜치

`part-1-environment → part-2-feed-api → … → part-9-resilience` 순서입니다. `main`은 현재 완성 코드예요. 챕터를 바꾸면 해당 폴더에서 `uv sync --locked`와 `uv run sns-recommend seed`를 실행합니다.

각 브랜치의 SNS 앱은 모노레포 전환 시점 코드입니다. [Spring 연결 예제](https://github.com/apieceofcoding/sns-server/blob/main/sns-recommend/integrations/sns-app/README.md)는 해당 파일이 있는 후반 챕터와 `main`에서 확인해요. 실제 SNS 원본과 추천 DB의 ID도 맞춰야 합니다.

강사용 문서, 슬라이드와 대본은 이 저장소에 포함하지 않습니다.
