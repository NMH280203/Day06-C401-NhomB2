# 🍜 FoodChat AI — Frontend

> Trợ lý AI thông minh giúp bạn tìm món ăn ngon và nhà hàng phù hợp gần bạn.

FoodChat AI là ứng dụng chatbot gợi ý món ăn & nhà hàng, sử dụng AI để phân tích sở thích, ngân sách và vị trí của người dùng nhằm đưa ra gợi ý phù hợp nhất.

---

## ✨ Tính năng chính

- 💬 **Chat AI thời gian thực** — Giao tiếp tự nhiên với AI qua giao diện chat, nhận gợi ý món ăn & nhà hàng theo ngữ cảnh.
- 🍕 **Gợi ý món ăn** — Hiển thị danh sách món ăn phù hợp với mô tả, giá dự kiến, lý do gợi ý và tags.
- 🏪 **Gợi ý nhà hàng** — Tìm quán ăn gần bạn với thông tin đánh giá, khoảng cách, món nổi bật và trạng thái mở/đóng.
- 🗺️ **Bản đồ tích hợp** — Xem vị trí nhà hàng trên Google Maps.
- 📍 **Định vị tự động** — Dùng geolocation để tìm quán gần nhất.
- 💾 **Lưu lịch sử chat** — Lịch sử trò chuyện được lưu trong localStorage, giữ nguyên khi reload.
- 📱 **Responsive** — Giao diện tối ưu cho cả desktop và mobile.

---

## 🛠️ Tech Stack

| Công nghệ | Phiên bản | Mô tả |
|---|---|---|
| [Next.js](https://nextjs.org/) | 14.x | Framework React với App Router |
| [React](https://react.dev/) | 18.x | UI library |
| [TypeScript](https://www.typescriptlang.org/) | 5.x | Type-safe JavaScript |
| [Tailwind CSS](https://tailwindcss.com/) | 3.x | Utility-first CSS framework |
| [Zustand](https://zustand-demo.pmnd.rs/) | 4.x | Lightweight state management |

---

## 📁 Cấu trúc thư mục

```
fe/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout (metadata, font, favicon)
│   ├── page.tsx                # Trang chủ — redirect tới /chat
│   ├── globals.css             # Global styles
│   └── chat/
│       ├── layout.tsx          # Layout cho trang chat
│       └── page.tsx            # Trang chat chính
│
├── components/                 # React components
│   ├── chat/                   # Components cho chat
│   │   ├── ChatWindow.tsx      # Cửa sổ chat chính
│   │   ├── MessageList.tsx     # Danh sách tin nhắn
│   │   ├── MessageBubble.tsx   # Bong bóng tin nhắn (user/assistant)
│   │   ├── MessageInput.tsx    # Input gửi tin nhắn
│   │   └── TypingIndicator.tsx # Hiệu ứng đang gõ
│   ├── results/                # Components hiển thị kết quả
│   │   ├── FoodCard.tsx        # Card món ăn
│   │   ├── FoodList.tsx        # Danh sách món ăn
│   │   ├── RestaurantCard.tsx  # Card nhà hàng
│   │   ├── RestaurantList.tsx  # Danh sách nhà hàng
│   │   └── ResultPanel.tsx     # Panel kết quả (tabs: Món ăn/Quán ăn/Bản đồ)
│   ├── map/
│   │   └── MapEmbed.tsx        # Google Maps embed
│   └── ui/                     # UI primitives
│       ├── Button.tsx
│       ├── Spinner.tsx
│       └── Badge.tsx
│
├── hooks/                      # Custom React hooks
│   ├── useChat.ts              # Logic gửi/nhận tin nhắn qua SSE
│   ├── useChatStore.ts         # Re-export chat store
│   └── useGeolocation.ts       # Lấy vị trí người dùng
│
├── lib/                        # Utilities & shared logic
│   ├── api.ts                  # API client (SSE chat + REST restaurants)
│   ├── storage.ts              # localStorage helpers
│   └── types.ts                # TypeScript type definitions
│
├── store/
│   └── chatStore.ts            # Zustand store (persist to localStorage)
│
├── .env.local                  # Biến môi trường (local)
├── next.config.js              # Cấu hình Next.js
├── tailwind.config.ts          # Cấu hình Tailwind CSS (custom colors, animations)
├── tsconfig.json               # Cấu hình TypeScript
├── postcss.config.js           # Cấu hình PostCSS
└── package.json                # Dependencies & scripts
```

---

## 🚀 Hướng dẫn cài đặt & chạy

### Yêu cầu hệ thống

- **Node.js** >= 18.x
- **npm** >= 9.x (hoặc yarn/pnpm)
- Backend API đang chạy tại `http://localhost:8000` (hoặc URL tùy chỉnh)

### 1. Cài đặt dependencies

```bash
cd fe
npm install
```

### 2. Cấu hình biến môi trường

Tạo file `.env.local` trong thư mục `fe/` (nếu chưa có):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_KEY=YOUR_GOOGLE_MAPS_API_KEY
```

| Biến | Mô tả | Bắt buộc |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL của Backend API | ✅ Có |
| `NEXT_PUBLIC_GOOGLE_MAPS_KEY` | Google Maps API key (dùng cho tab Bản đồ) | ⚠️ Không bắt buộc, nhưng cần để hiển thị bản đồ |

### 3. Chạy Development Server

```bash
npm run dev
```

Mở trình duyệt tại **[http://localhost:3000](http://localhost:3000)** — trang sẽ tự động chuyển đến `/chat`.

### 4. Build Production

```bash
npm run build
npm start
```

---

## 📜 Danh sách Scripts

| Script | Lệnh | Mô tả |
|---|---|---|
| `dev` | `npm run dev` | Chạy dev server (hot reload) |
| `build` | `npm run build` | Build production bundle |
| `start` | `npm start` | Chạy production server |
| `lint` | `npm run lint` | Kiểm tra lỗi ESLint |

---

## 🔌 Kết nối với Backend

Frontend giao tiếp với Backend qua 2 endpoint:

### `POST /api/chat` — Chat AI (SSE)

Gửi tin nhắn và nhận phản hồi qua **Server-Sent Events (SSE)**:

```
Request Body:
{
  "messages": [...],    // Lịch sử tin nhắn
  "context": {...}      // Ngữ cảnh người dùng (vị trí, ngân sách, v.v.)
}

SSE Events:
  event: thinking             → Trạng thái đang xử lý
  event: food_results         → Danh sách món ăn gợi ý
  event: restaurant_results   → Danh sách nhà hàng gợi ý
  event: text                 → Nội dung phản hồi (streaming)
  event: ask_context          → Yêu cầu thêm thông tin từ user
  event: done                 → Hoàn thành + gợi ý câu hỏi tiếp theo
  event: error                → Thông báo lỗi
```

### `GET /api/restaurants` — Tìm nhà hàng

```
Query Params: ?lat=...&lng=...&query=...&budget=...&radius=...&limit=...
Response: { restaurants: Restaurant[], total: number }
```

### 🧪 Chạy không cần Backend (Mock Mode)

File `lib/api.ts` có sẵn hàm `mockSendMessage()` để test FE độc lập. Hàm này trả về dữ liệu giả lập với hiệu ứng SSE streaming, bao gồm:
- 3 món ăn mẫu (Phở Bò, Bún Chả, Cơm Tấm)
- 3 nhà hàng mẫu (Phở Thìn, Bún Chả Hương Liên, Cơm Tấm Bụi)

Để sử dụng mock, thay `sendMessage` bằng `mockSendMessage` trong hook `useChat.ts`.

---

## 🎨 Design System

### Color Palette

| Token | Hex | Dùng cho |
|---|---|---|
| `primary-500` | `#ff4f0a` | Accent chính, nút bấm, user bubble |
| `surface-50` | `#f8f9fa` | Background sáng |
| `surface-900` | `#212529` | Text chính |
| `accent-emerald` | `#10b981` | Trạng thái mở cửa, thành công |
| `accent-amber` | `#f59e0b` | Rating sao, cảnh báo |
| `accent-rose` | `#f43f5e` | Đóng cửa, lỗi |

### Custom Animations

- `fade-in` — Hiệu ứng hiện dần
- `slide-up` — Trượt lên từ dưới
- `slide-in-right` — Trượt vào từ phải
- `pulse-dot` — Hiệu ứng typing indicator
- `bounce-in` — Nảy vào
- `shimmer` — Hiệu ứng skeleton loading

---

## 📝 Ghi chú

- **Không có Auth / Database** — Toàn bộ state lưu trong `localStorage` (key: `food-chat-store`).
- **TypeScript strict** — Không sử dụng `any`, toàn bộ code type-safe.
- **SSE streaming** — Phản hồi từ AI được stream realtime, không phải đợi toàn bộ response.

---

*FoodChat AI — Batch 02 · AI Product Labs · Day 05–06*
