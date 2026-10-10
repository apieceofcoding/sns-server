# Spring SNS 연결 예제

기존 SNS에 추천 조회와 이벤트 전달을 추가하는 예제입니다. 별도 실행 앱은 아니에요.

## 적용 순서

1. 기존 mock `RecommendClient`를 정리하고 `src/main/java/`의 파일을 SNS 앱에 적용합니다. 같은 빈 이름을 함께 등록하지 않아요.
2. `sql/outbox.sql`을 SNS DB에 적용하고 Spring 스케줄링을 활성화합니다. `uv run sns-recommend init`도 같은 구조를 준비해요.
3. 글 작성, 수정, 삭제와 복구 트랜잭션 안에서 `posts.content_version`을 1 올리고 `RecommendationOutbox.append`를 호출합니다. 좋아요 수 변경은 버전을 올리지 않아요.
4. `recommend.url`과 `recommend.token`을 맞춥니다. 사용자와 게시글은 복사하지 않으며, 추천 서비스가 같은 ID로 SNS DB를 읽어요.
5. 로그인 후 `/api/v1/recommendations`를 추천 탭에 연결합니다.

## 처리 규칙

| 구간 | 규칙 |
|---|---|
| 조회 | 추천 ID 순서로 원본 조립, 삭제와 접근 권한 재확인 |
| 첫 조회 실패 | 최신순 대체, 별도의 `latest:` 커서 사용 |
| 추천 세션 중 실패 | 오류 반환 후 새 세션 시작 |
| 행동 | 실제 노출, 클릭, 좋아요와 관심 없음 전송. 사용자 ID는 로그인 정보에서 결정 |
| Outbox | 원본 변경과 같은 트랜잭션에서 기록. `MANDATORY` 적용 |
| 이벤트 내용 | 글 ID와 버전만 전달. 본문, 작성자와 좋아요 수는 보내지 않음 |

삭제는 `RecommendationOutbox.deleted`로 전달합니다. 비공개, 차단과 뮤트를 추가한다면 원본 조회에도 같은 정책을 적용해요. 전체 UI 연결과 사용자 시나리오는 별도 검증이 필요합니다.
