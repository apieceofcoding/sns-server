# 5. 개인화 후보 검색

저장된 관심사 벡터로 검색하고 최신순과 인기순 후보를 합칩니다. 노출, 관심 없음, 삭제와 오래된 게시글을 제외해요.

```sh
uv sync --locked
uv run sns-recommend index
uv run sns-recommend embedding --user 1
uv run sns-recommend embedding --user 2
uv run uvicorn sns_recommend.api:app --port 8001
```

두 사용자의 추천 ID를 비교합니다. 신규 사용자는 명시한 관심사와 최신순 후보로 시작해요. likes/clicks 이벤트는 저장된 게시글 벡터로 관심사를 갱신합니다. 모델과 벡터 공간이 다른 결과는 섞지 않습니다.

200개 규모에서는 pgvector의 정확 검색을 사용합니다. 대규모 ANN 인덱스 최적화는 이번 실습에 포함하지 않아요.

`seed` 실행 시 테이블도 준비합니다. DB 서버는 먼저 실행해 주세요. 기존 데이터는 유지하고 없는 ID만 추가합니다.

