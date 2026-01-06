import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    // 로컬 개발 환경에서 사용할 환경 변수
    // 로컬에서는 localhost:8080, 배포 시에는 Vercel 환경 변수 사용
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
};

export default nextConfig;
