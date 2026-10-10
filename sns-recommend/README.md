# 7. LangGraph 추천 생성과 복구

앞에서 만든 함수를 StateGraph 노드로 연결합니다. 상태는 PostgreSQL에, 완성된 목록은 Redis에 저장해요.

```sh
uv sync --locked
uv run sns-recommend init
uv run sns-recommend graph --user 1 --pause-after-rerank
uv run python -m sns_recommend.worker --once
uv run sns-recommend graph --user 2
uv run pytest
```

첫 명령은 재정렬 노드의 체크포인트 저장 후 작업을 멈추고 lease를 만료시킵니다. 다음 worker가 같은 작업 ID로 검증부터 재개해요. 모델 응답과 체크포인트 저장 사이의 장애에서는 호출이 반복될 수 있습니다.

작업 예약과 lease는 DB 작업 테이블, 단계 상태는 LangGraph, 멱등 발행은 우리 Redis 코드가 담당해요. 새로운 생성 세대가 예약되면 오래된 결과는 발행하지 않습니다.
