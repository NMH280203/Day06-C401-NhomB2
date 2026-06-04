import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "FoodieAI - Trợ Lý Gợi Ý Món Ăn & Nhà Hàng",
  description: "Trợ lý AI gợi ý món ăn ngon, đặc sản địa phương và nhà hàng phù hợp với khẩu vị, vị trí và ngân sách của bạn.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark scroll-smooth">
      <body
        className={`${inter.variable} font-sans bg-slate-950 text-slate-100 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
