import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 런타임에 환경변수를 읽도록 env 설정 제거
  // API 라우트에서 직접 process.env.NEWS_API_URL을 사용
};

export default nextConfig;
