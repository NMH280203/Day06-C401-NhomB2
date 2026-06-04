import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FoodChat AI — Gợi ý Món Ăn & Nhà Hàng",
  description:
    "Trợ lý AI thông minh giúp bạn tìm món ăn ngon và nhà hàng phù hợp gần bạn. Gợi ý dựa trên sở thích, ngân sách và vị trí.",
  keywords: ["food", "restaurant", "AI", "chatbot", "gợi ý món ăn", "nhà hàng"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍜</text></svg>" />
      </head>
      <body className="h-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}
