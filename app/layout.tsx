import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI-Place-Mate — 로컬 시각 프로토타입",
  description: "조건을 말하면 근거가 붙은 세 곳이 온다",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="bg-muted min-h-full">
        {/* R5 완화 — 화면이 확정된 것으로 굳는 것을 막는다.
            고지 배너(N1~N3)와 혼동되지 않도록 콘텐츠 밖 최상단에 둔다. */}
        <p className="bg-foreground text-background px-4 py-1 text-center text-[11px] tracking-tight">
          픽스처 기반 프로토타입 · 화면 미확정
        </p>
        {/* 모바일 1폭(390px)만 맞춘다. 데스크톱에서도 같은 폭으로 보인다. */}
        <div className="bg-background mx-auto min-h-full w-full max-w-[390px] border-x">
          {children}
        </div>
      </body>
    </html>
  );
}
