# Spring SNS 연결 예제

추천 조회는 [SNS 앱](../../../sns-app/README.md#추천-연결)의 `RecommendationClient`와 `/api/v1/recommendations`를 사용합니다. 이 폴더의 `RecommendClient`, `RecommendationController`, `RecommendationPostRepository`는 참고용이며 앱에 복사하지 않아요.

## 게시글 이벤트 전달

1. `RecommendationOutbox`와 `RecommendationOutboxRelay`를 SNS 앱에 적용합니다.
2. `sql/outbox.sql`을 SNS DB에 적용합니다. `uv run sns-recommend init`도 같은 구조를 준비해요.
3. 글 작성, 수정, 삭제와 복구 트랜잭션 안에서 `posts.content_version`을 1 올리고 `RecommendationOutbox.append`를 호출합니다. 좋아요 수 변경은 버전을 올리지 않아요.
4. relay의 `recommend.url`과 `recommend.token`을 추천 API 주소와 내부 토큰에 맞춥니다. Docker에서는 호스트의 API 주소를 사용해요.

| 항목 | 규칙 |
|---|---|
| Outbox 기록 | 원본 변경과 같은 트랜잭션, `MANDATORY` 적용 |
| 이벤트 내용 | 글 ID와 버전만 전달 |
| 삭제 | `RecommendationOutbox.deleted` 사용 |
| 행동 이벤트 | 로그인한 사용자 ID로 노출, 클릭, 좋아요와 관심 없음 전달 |

화면의 추천 탭은 `/api/v1/recommendations`를 호출하도록 연결합니다. 비공개, 차단과 뮤트를 추가할 때는 원본 조회에도 해당 정책을 적용해요.
