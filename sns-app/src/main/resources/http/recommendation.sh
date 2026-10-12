#!/bin/bash

BASE_URL="http://localhost:8080"

echo "추천 피드 조회 (로그인 쿠키 필요)"
curl -fsS -b cookies.txt "${BASE_URL}/api/v1/recommendations?limit=20"

if [ -n "${1:-}" ]; then
  echo "다음 페이지 조회"
  curl -fsS -b cookies.txt --get "${BASE_URL}/api/v1/recommendations" \
    --data-urlencode "cursor=$1" --data-urlencode "limit=20"
fi
