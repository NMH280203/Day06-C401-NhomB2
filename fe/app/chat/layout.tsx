import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chat — FoodChat AI",
  description: "Trò chuyện với AI để tìm món ăn ngon và nhà hàng phù hợp gần bạn.",
};

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
