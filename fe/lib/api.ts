import type {
  ChatPayload,
  FoodSuggestion,
  Restaurant,
  RestaurantQueryParams,
  RestaurantResponse,
  SSECallbacks,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── SSE Parser ────────────────────────────────────────────────────────────────
function parseSSELine(line: string): { event: string; data: string } | null {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith(":")) return null;

  if (trimmed.startsWith("event:")) {
    return { event: trimmed.slice(6).trim(), data: "" };
  }
  if (trimmed.startsWith("data:")) {
    return { event: "", data: trimmed.slice(5).trim() };
  }
  return null;
}

// ─── Send Message (SSE) ────────────────────────────────────────────────────────
/** Strip FE-only fields so FastAPI ChatRequest validates. */
function toBackendPayload(payload: ChatPayload): {
  messages: { role: "user" | "assistant"; content: string }[];
  context: ChatPayload["context"];
} {
  return {
    messages: payload.messages
      .filter((m) => m.role === "user" || m.content.trim().length > 0)
      .map(({ role, content }) => ({ role, content })),
    context: payload.context,
  };
}

export async function sendMessage(
  payload: ChatPayload,
  callbacks: SSECallbacks
): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toBackendPayload(payload)),
    });

    if (!response.ok) {
      callbacks.onError(`Server error: ${response.status}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      callbacks.onError("No response stream available");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";
    let currentEvent = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const parsed = parseSSELine(line);
        if (!parsed) continue;

        if (parsed.event) {
          currentEvent = parsed.event;
          continue;
        }

        if (parsed.data && currentEvent) {
          handleSSEEvent(currentEvent, parsed.data, callbacks);
          currentEvent = "";
        }
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      const lines = buffer.split("\n");
      for (const line of lines) {
        const parsed = parseSSELine(line);
        if (!parsed) continue;
        if (parsed.event) currentEvent = parsed.event;
        if (parsed.data && currentEvent) {
          handleSSEEvent(currentEvent, parsed.data, callbacks);
          currentEvent = "";
        }
      }
    }
  } catch (err) {
    callbacks.onError(
      err instanceof Error ? err.message : "Network error occurred"
    );
  }
}

function handleSSEEvent(
  event: string,
  data: string,
  callbacks: SSECallbacks
): void {
  let parsed: unknown;
  try {
    parsed = JSON.parse(data);
  } catch {
    parsed = data;
  }

  switch (event) {
    case "thinking": {
      const obj = parsed as { status?: string };
      callbacks.onThinking(
        typeof obj === "object" && obj !== null && obj.status
          ? String(obj.status)
          : String(parsed)
      );
      break;
    }
    case "food_results": {
      const obj = parsed as { foods?: FoodSuggestion[] };
      const foods = Array.isArray(parsed)
        ? (parsed as FoodSuggestion[])
        : obj.foods ?? [];
      callbacks.onFoodResults(foods);
      break;
    }
    case "restaurant_results": {
      const obj = parsed as { restaurants?: Restaurant[] };
      const restaurants = Array.isArray(parsed)
        ? (parsed as Restaurant[])
        : obj.restaurants ?? [];
      callbacks.onRestaurantResults(restaurants);
      break;
    }
    case "text": {
      const obj = parsed as { delta?: string };
      const delta =
        typeof obj === "object" && obj !== null && "delta" in obj
          ? String(obj.delta ?? "")
          : String(parsed);
      if (delta) callbacks.onTextDelta(delta);
      break;
    }
    case "ask_context": {
      const obj = parsed as {
        field?: string;
        message?: string;
        missing_fields?: string[];
      };
      callbacks.onAskContext(
        obj.field ?? "context",
        obj.message ?? "Bạn cho mình thêm thông tin nhé?",
        obj.missing_fields
      );
      break;
    }
    case "done": {
      const obj = parsed as { follow_up_suggestions?: string[] };
      const suggestions = Array.isArray(parsed)
        ? (parsed as string[])
        : obj.follow_up_suggestions ?? [];
      callbacks.onDone(suggestions);
      break;
    }
    case "error": {
      const obj = parsed as { message?: string };
      console.error("[chat] server error:", obj?.message ?? parsed);
      callbacks.onError(
        "Xin lỗi, mình chưa xử lý được yêu cầu lúc này. Bạn thử gửi lại sau vài giây nhé!"
      );
      break;
    }
  }
}

// ─── Get Restaurants ───────────────────────────────────────────────────────────
export async function getRestaurants(
  params: RestaurantQueryParams
): Promise<RestaurantResponse> {
  const searchParams = new URLSearchParams();
  searchParams.set("lat", String(params.lat));
  searchParams.set("lng", String(params.lng));
  if (params.query) searchParams.set("query", params.query);
  if (params.budget) searchParams.set("budget", String(params.budget));
  if (params.radius) searchParams.set("radius", String(params.radius));
  if (params.limit) searchParams.set("limit", String(params.limit));

  const response = await fetch(
    `${API_URL}/api/restaurants?${searchParams.toString()}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch restaurants: ${response.status}`);
  }
  return (await response.json()) as RestaurantResponse;
}

// ─── Mock SSE (for testing without BE) ─────────────────────────────────────────
export async function mockSendMessage(
  _payload: ChatPayload,
  callbacks: SSECallbacks
): Promise<void> {
  const delay = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  callbacks.onThinking("Đang phân tích yêu cầu của bạn...");
  await delay(600);

  callbacks.onThinking("Đang tìm món ăn phù hợp...");
  await delay(800);

  const mockFoods: FoodSuggestion[] = [
    {
      name: "Phở Bò Tái Nạm",
      category: "Món nước",
      description:
        "Phở bò truyền thống với nước dùng ninh xương 12 tiếng, thịt bò tái mềm và nạm giòn.",
      estimated_price: 55000,
      reason:
        "Món ăn sáng kinh điển, phù hợp với thời tiết và budget của bạn.",
      tags: ["Truyền thống", "Bổ dưỡng", "Ăn sáng"],
    },
    {
      name: "Bún Chả Hà Nội",
      category: "Món khô",
      description:
        "Bún chả với thịt nướng than hoa, nước mắm chua ngọt, rau sống tươi.",
      estimated_price: 50000,
      reason: "Vị ngon đậm đà, phần ăn vừa đủ cho một người.",
      tags: ["Đặc sản", "Nướng", "Ăn trưa"],
    },
    {
      name: "Cơm Tấm Sườn Bì Chả",
      category: "Cơm",
      description:
        "Cơm tấm với sườn nướng mật ong, bì, chả trứng, đồ chua và nước mắm.",
      estimated_price: 45000,
      reason: "Món ăn no lâu, giá hợp lý, phù hợp ăn trưa.",
      tags: ["Sài Gòn", "No lâu", "Ăn trưa"],
    },
  ];

  callbacks.onFoodResults(mockFoods);
  await delay(500);

  const mockRestaurants: Restaurant[] = [
    {
      place_id: "mock_1",
      name: "Phở Thìn Bờ Hồ",
      address: "13 Lò Đúc, Hai Bà Trưng, Hà Nội",
      distance_km: 1.2,
      rating: 4.5,
      price_level: 2,
      is_open: true,
      phone: "024-3821-2709",
      maps_url: "https://maps.google.com/?q=Phở+Thìn+Bờ+Hồ",
      featured_dishes: ["Phở Bò Tái", "Phở Bò Chín", "Phở Đặc Biệt"],
      score: 92,
    },
    {
      place_id: "mock_2",
      name: "Bún Chả Hương Liên",
      address: "24 Lê Văn Hưu, Hai Bà Trưng, Hà Nội",
      distance_km: 0.8,
      rating: 4.3,
      price_level: 2,
      is_open: true,
      maps_url: "https://maps.google.com/?q=Bún+Chả+Hương+Liên",
      featured_dishes: ["Bún Chả Obama", "Bún Chả Thường", "Nem Rán"],
      score: 88,
    },
    {
      place_id: "mock_3",
      name: "Cơm Tấm Bụi Sài Gòn",
      address: "84 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội",
      distance_km: 2.1,
      rating: 4.1,
      price_level: 1,
      is_open: false,
      phone: "024-3933-1234",
      maps_url: "https://maps.google.com/?q=Cơm+Tấm+Bụi+Sài+Gòn",
      featured_dishes: [
        "Cơm Tấm Sườn",
        "Cơm Tấm Đặc Biệt",
        "Chả Giò",
      ],
      score: 78,
    },
  ];

  callbacks.onRestaurantResults(mockRestaurants);
  await delay(500);

  const responseText =
    "Dựa trên yêu cầu của bạn, mình gợi ý **3 món ăn** phù hợp nhé! 🍜\n\nCả ba món đều là đặc sản Việt Nam, giá cả hợp lý và rất phổ biến. Mình cũng đã tìm được một số quán gần bạn rồi. Bạn có thể xem chi tiết ở bên phải nhé!";

  for (const char of responseText) {
    callbacks.onTextDelta(char);
    await delay(15);
  }

  await delay(300);

  callbacks.onDone([
    "Tìm thêm món chay",
    "Quán nào gần nhất?",
    "Có món gì cho 2 người không?",
    "Gợi ý món tráng miệng",
  ]);
}
