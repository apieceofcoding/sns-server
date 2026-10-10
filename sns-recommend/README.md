# 3. 게시글과 행동 전달

2단계의 조회 경로에 이벤트 접수와 작업 테이블을 추가합니다. 중복 이벤트와 오래된 게시글 버전을 구분해요.

```sh
uv sync --locked
uv run sns-recommend source-post --post 1001
uv run uvicorn sns_recommend.api:app --port 8001
```

다른 터미널에서 `uv run sns-recommend relay`를 두 번 실행합니다. 첫 실행은 1건, 두 번째는 0건 전달해요. 전송 후 응답을 받기 전에 중단되면 다시 전달되며, 수신자가 이벤트 ID로 중복을 제거합니다.

Outbox 시연은 별도 `source_demo` 스키마를 사용합니다. 실제 SNS에서는 원본 SNS DB의 트랜잭션과 Outbox를 사용해요. 이 단계는 작업을 저장하며 worker 실행은 다음 단계에서 추가합니다.

`seed` 실행 시 테이블도 준비합니다. DB 서버는 먼저 실행해 주세요. 기존 데이터는 유지하고 없는 ID만 추가합니다.

