# 기존 Spring SNS 연결

확인한 `deploy-observability/sns-app`에 적용할 별도 예제입니다. 원본은 변경하지 않았어요.

1. 원본 SNS의 실습 복사본에 `src/main/java/` 아래 파일을 복사합니다.
2. `sql/outbox.sql`을 SNS DB에 적용하고 Spring의 스케줄링을 활성화합니다.
3. 게시글 생성, 수정과 삭제 서비스의 트랜잭션 안에서 `RecommendationOutbox.append`를 호출해요. 게시글 버전은 SNS DB에서 단조 증가하도록 추가합니다.
4. `recommend.url`과 `recommend.token`을 추천 API와 맞춥니다.
5. 로그인 후 `/api/v1/recommendations`를 호출합니다. 기존 타임라인 화면의 추천 탭에서 이 주소를 사용해요.

조회는 전달된 ID 순서를 복원하고 원본 삭제를 다시 검사합니다. 첫 조회 실패는 최신순으로 대체하며 `latest:` 커서를 별도로 사용해요. 추천 세션 중 실패하면 새 세션을 시작하도록 오류를 반환합니다.

노출은 실제 화면에 보인 뒤 전송하고, 클릭과 좋아요, 관심 없음은 별도 이벤트로 보냅니다. 사용자 ID는 로그인 정보에서 정합니다. 비공개, 차단과 뮤트 기능을 추가한다면 원본 조회에도 동일 접근 정책을 적용해야 해요.

Outbox 예제는 `MANDATORY` 트랜잭션을 요구합니다. 서비스에 단순히 HTTP 호출만 추가하면 원본 저장과 이벤트 저장을 함께 보장할 수 없습니다. 삭제는 `post.deleted`, 행동은 해당 kind와 user_id, post_id를 가진 이벤트를 append합니다.

이 자료는 적용 예제이며 원본의 전체 UI 연동과 사용자 시나리오 검증은 별도 수행해야 합니다.
