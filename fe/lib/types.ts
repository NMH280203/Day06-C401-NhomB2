// ─── Location ──────────────────────────────────────────────────────────────────
export interface Location {
  lat: number;
  lng: number;
  address?: string;
}

// ─── User Context ──────────────────────────────────────────────────────────────
export interface UserContext {
  location?: Location;
  budget?: number; // VND
  people?: number;
  meal_time?: "breakfast" | "lunch" | "dinner" | "snack";
  purpose?: "family" | "date" | "friends" | "work" | "solo";
  preferences?: string[];
  allergies?: string[];
}

// ─── Message ───────────────────────────────────────────────────────────────────
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  foods?: FoodSuggestion[];
  restaurants?: Restaurant[];
  follow_up_suggestions?: string[];
  status?: string; // trạng thái thinking
}

// ─── Food Suggestion ───────────────────────────────────────────────────────────
export interface FoodSuggestion {
  name: string;
  category: string;
  description: string;
  estimated_price: number;
  reason: string;
  tags: string[];
}

// ─── Restaurant ────────────────────────────────────────────────────────────────
export interface Restaurant {
  place_id: string;
  name: string;
  address: string;
  distance_km: number;
  rating: number;
  price_level: number; // 1–4
  is_open: boolean;
  phone?: string;
  maps_url: string;
  photo_url?: string;
  featured_dishes: string[];
  score: number;
}

// ─── Chat Store ────────────────────────────────────────────────────────────────
export interface ChatStore {
  messages: Message[];
  context: UserContext;
  isLoading: boolean;
  currentStatus: string;
  results: {
    foods: FoodSuggestion[];
    restaurants: Restaurant[];
  };
  addMessage: (msg: Message) => void;
  updateLastAssistantMessage: (patch: Partial<Message>) => void;
  setContext: (ctx: Partial<UserContext>) => void;
  setLoading: (v: boolean) => void;
  setStatus: (s: string) => void;
  setResults: (foods: FoodSuggestion[], restaurants: Restaurant[]) => void;
  appendToLastAssistantContent: (delta: string) => void;
  clearHistory: () => void;
}

// ─── SSE Callbacks ─────────────────────────────────────────────────────────────
export interface SSECallbacks {
  onThinking: (status: string) => void;
  onFoodResults: (foods: FoodSuggestion[]) => void;
  onRestaurantResults: (restaurants: Restaurant[]) => void;
  onTextDelta: (delta: string) => void;
  onAskContext: (field: string, message: string) => void;
  onDone: (follow_up_suggestions: string[]) => void;
  onError: (message: string) => void;
}

// ─── API Payload ───────────────────────────────────────────────────────────────
export interface ChatPayload {
  messages: Message[];
  context: UserContext;
}

// ─── Restaurant Query Params ───────────────────────────────────────────────────
export interface RestaurantQueryParams {
  lat: number;
  lng: number;
  query?: string;
  budget?: number;
  radius?: number;
  limit?: number;
}

export interface RestaurantResponse {
  restaurants: Restaurant[];
  total: number;
}
