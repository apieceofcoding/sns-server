# 1. 실습 환경

로컬 PostgreSQL과 Redis, 합성 게시글 200개와 사용자 3명을 준비합니다.

```sh
uv sync --locked
docker compose up -d --wait
uv run sns-recommend seed
uv run sns-recommend status
uv run pytest
```

`posts: 200`, `users: 3`을 확인해요. 기존 SNS 프로젝트와 다른 포트를 사용합니다.

자료: [도메인](../materials/domain/01-environment.md), [실습](../materials/labs/01-environment.md).

`seed` 실행 시 테이블도 준비합니다. DB 서버는 먼저 실행해 주세요. 기존 데이터는 유지하고 없는 ID만 추가합니다.

