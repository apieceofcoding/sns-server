# SNS 추천 서비스 실습

기존 SNS에 추천 피드를 추가하는 강의 저장소입니다. 최신순, 인기순, 임베딩 기반 추천과 LLM 재정렬을 단계적으로 비교해요.

## 구성

| 폴더 | 역할 |
|---|---|
| [sns-front](sns-front/README.md) | Next.js 기반 SNS 화면 |
| [sns-app](sns-app/README.md) | Spring Boot 기반 로그인, 게시글과 피드 API |
| [sns-recommend](sns-recommend/README.md) | Python 기반 추천 생성과 조회 API |

추천 작업이 목록을 미리 만들어 Redis에 저장합니다. SNS 앱은 추천 API에서 받은 ID 순서대로 게시글을 응답해요. 피드 조회 중에는 모델을 호출하지 않습니다.

## 시작하기

```sh
git clone https://github.com/apieceofcoding/sns-service.git
cd sns-service
```

[환경 준비와 실습 순서](sns-recommend/README.md)에 따라 part-1부터 part-9까지 진행해요. 기본 실습은 모의 모델을 사용하므로 API 키와 호출 비용이 필요 없습니다.
