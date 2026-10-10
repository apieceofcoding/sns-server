# SNS 화면

Next.js로 로그인, 게시글과 타임라인 화면을 제공합니다. [전체 실습 순서](../README.md#실습-순서)를 따릅니다.

```sh
# sns-front/에서 실행
npm ci
npm run dev
# 브라우저: http://localhost:3000
# 종료: Ctrl+C
```

Node.js LTS와 npm을 사용합니다. 먼저 SNS 앱을 실행해요. API 기본 주소는 `http://localhost:8080`이며 `.env.local`의 `NEXT_PUBLIC_API_BASE_URL`로 바꿀 수 있습니다.

원본: [springboot-sns-sample-front](https://github.com/apieceofcoding/springboot-sns-sample-front). 원본 main을 Git subtree로 가져와 이 저장소에서 함께 관리합니다.
