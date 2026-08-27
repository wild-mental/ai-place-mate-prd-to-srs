import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 스크린샷이 평가 대상이다. dev 오버레이가 화면을 가리므로 끈다.
  devIndicators: false,
  /* config options here */
};

export default nextConfig;
