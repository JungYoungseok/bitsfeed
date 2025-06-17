import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 환경변수 설정
  env: {
    NEWS_API_URL: process.env.NEWS_API_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
