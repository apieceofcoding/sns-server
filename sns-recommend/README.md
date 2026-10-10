# 6. Gemini 재정렬

검색 후보를 한 번에 전달하고 ID 순서만 받습니다. 결과가 후보의 순열인지 검사한 뒤 다양성을 조정해요.

```sh
uv sync --locked
uv run sns-rec init
uv run sns-rec generate --user 1
uv run pytest
```

기본값은 합성 fixture이며 `fixture_llm`로 표시합니다. 실제 Gemini를 호출하지 않아요. 실제 호출은 `.env`에 `MODEL_MODE=live`와 개인 `GOOGLE_API_KEY`를 설정합니다. 무료 한도를 확인한 뒤 합성 데이터만 사용합니다.

시간 초과, 잘못된 ID와 출력 오류는 `rules_fallback`으로 대체합니다. 순위는 클릭 확률이 아닙니다. `record`로 저장한 실제 결과만 `replay` 모드에서 재생해요.
