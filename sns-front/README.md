# SNS 화면

Next.js로 로그인, 게시글과 타임라인 화면을 제공합니다.

Node.js LTS와 npm을 준비하고 [SNS 앱](../sns-app/README.md#실행)을 먼저 실행해요. 별도 터미널의 `sns-front/`에서 실행합니다.

```sh
npm ci
npm run dev
```

[화면 열기](http://localhost:3000)에서 가입과 로그인을 확인합니다. 종료는 `Ctrl+C`예요.

API 기본 주소는 `http://localhost:8080`이며 `.env.local`의 `NEXT_PUBLIC_API_BASE_URL`로 바꿀 수 있습니다.
