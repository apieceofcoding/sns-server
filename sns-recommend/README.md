# 1. 실습 환경

로컬 PostgreSQL과 Redis, 합성 게시글 200개와 사용자 3명을 준비합니다.

```sh
uv sync --locked
docker compose up -d --wait
uv run sns-rec init
uv run sns-rec seed
uv run sns-rec status
uv run pytest
```

`posts: 200`, `users: 3`을 확인해요. 기존 SNS 프로젝트와 다른 포트를 사용합니다.

자료: [도메인](../materials/domain/01-environment.md), [실습](../materials/labs/01-environment.md).
