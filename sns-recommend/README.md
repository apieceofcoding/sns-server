# 4. 게시글 색인

LangChain Document와 임베딩 인터페이스로 글을 준비하고 pgvector에 저장합니다.

```sh
uv sync --locked
uv run sns-recommend seed
uv run sns-recommend index
uv run python -m sns_recommend.worker --once
uv run pytest
```

기본 `MODEL_MODE=fixture`는 합성 주제 벡터입니다. Gemini의 실제 출력이 아니에요. `live`는 실제 호출, `record`는 호출과 응답 저장, `replay`는 저장 파일 재생입니다. live/record는 호출당 최대 20개 글부터 처리합니다. 여러 번 `index`를 실행해 나머지를 처리해요.

모델과 차원이 다른 벡터는 검색에 섞지 않습니다. 수정 중 완료된 오래된 임베딩 결과는 버전 검사로 저장하지 않아요.

`seed` 실행 시 테이블도 준비합니다. DB 서버는 먼저 실행해 주세요. 기존 데이터는 유지하고 없는 ID만 추가합니다.

