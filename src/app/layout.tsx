import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "경험을 담은 자기소개서",
  description: "나의 경험으로 작성하고, 비교하고, 다듬는 자기소개서 초안",
};

export default function RootLayout({ children }: { readonly children: ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
