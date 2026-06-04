import type { UserContext } from "./types";

/** Trích context từ câu user (đồng bộ logic với be/services/context_gaps.py). */

const AREA_HINTS: Record<string, { lat: number; lng: number; address: string }> = {
  "quận 1": { lat: 10.7769, lng: 106.7009, address: "Quận 1, TP.HCM" },
  "quận 7": { lat: 10.734, lng: 106.7217, address: "Quận 7, TP.HCM" },
  "bình thạnh": { lat: 10.8106, lng: 106.7091, address: "Bình Thạnh, TP.HCM" },
  "hoàn kiếm": { lat: 21.0285, lng: 105.8542, address: "Hoàn Kiếm, Hà Nội" },
  "cầu giấy": { lat: 21.0333, lng: 105.794, address: "Cầu Giấy, Hà Nội" },
  "hà nội": { lat: 21.0285, lng: 105.8542, address: "Hà Nội" },
  "sài gòn": { lat: 10.7769, lng: 106.7009, address: "TP.HCM" },
  "tp.hcm": { lat: 10.7769, lng: 106.7009, address: "TP.HCM" },
  "đà nẵng": { lat: 16.0544, lng: 108.2022, address: "Đà Nẵng" },
};

function parseBudget(text: string): number | undefined {
  let m = text.match(/(\d+(?:[.,]\d+)?)\s*triệu/i);
  if (m) return Math.round(parseFloat(m[1].replace(",", ".")) * 1_000_000);
  m = text.match(/(\d+)\s*k\b/i);
  if (m) return parseInt(m[1], 10) * 1000;
  m = text.match(/(\d{2,3})\s*(?:k|nghìn|ngàn)/i);
  if (m) return parseInt(m[1], 10) * 1000;
  m = text.match(/\b(\d{4,7})\b/);
  if (m) {
    const v = parseInt(m[1], 10);
    return v < 500_000 ? v : Math.min(v, 500_000);
  }
  return undefined;
}

function parseMealTime(text: string): UserContext["meal_time"] | undefined {
  const t = text.toLowerCase();
  if (/(sáng|breakfast)/.test(t)) return "breakfast";
  if (/(trưa|lunch)/.test(t)) return "lunch";
  if (/(tối|chiều|dinner)/.test(t)) return "dinner";
  if (/(xế|snack|vặt|uống)/.test(t)) return "snack";
  return undefined;
}

function parsePeople(text: string): number | undefined {
  let m = text.match(/(\d+)\s*người/i);
  if (m) return parseInt(m[1], 10);
  m = text.match(/(\d+)\s*ng\b/i);
  if (m) return parseInt(m[1], 10);
  if (/(một mình|1 mình|solo|alone)/i.test(text)) return 1;
  if (/đôi|2 người/i.test(text)) return 2;
  return undefined;
}

function parseLocation(text: string): UserContext["location"] | undefined {
  const t = text.toLowerCase();
  for (const [key, loc] of Object.entries(AREA_HINTS)) {
    if (t.includes(key)) {
      return { lat: loc.lat, lng: loc.lng, address: loc.address };
    }
  }
  return undefined;
}

function parsePreferences(text: string): string[] {
  const prefs: string[] = [];
  const t = text.toLowerCase();
  const map: [RegExp, string][] = [
    [/healthy|eat clean/i, "healthy"],
    [/ăn nhẹ|nhẹ/i, "light"],
    [/không cay|không ớt/i, "no_spicy"],
    [/chay|vegetarian/i, "vegetarian"],
    [/view đẹp/i, "scenic"],
    [/yên tĩnh|làm việc/i, "work_friendly"],
    [/cay nồng|món cay|\bcay\b/i, "cay"],
    [/ngọt|\bngot\b/i, "ngot"],
    [/chua ngọt|\bchua\b/i, "chua"],
    [/mặn|\bman\b/i, "man"],
    [/béo|đậm đà/i, "beo"],
    [/thanh|nhẹ vị/i, "nhat"],
    [/đắng/i, "dang"],
  ];
  for (const [re, val] of map) {
    if (re.test(t)) prefs.push(val);
  }
  return prefs;
}

function parseAllergies(text: string): string[] {
  const allergies: string[] = [];
  const terms = ["hải sản", "gluten", "lactose", "đậu nành", "tôm", "cua", "đỗ"];
  const t = text.toLowerCase();
  for (const term of terms) {
    if (t.includes(term)) allergies.push(term);
  }
  return allergies;
}

/** Gộp thông tin mới từ tin nhắn vào context hiện tại. */
export function mergeContextFromMessage(
  current: UserContext,
  text: string,
  preferField?: string | null
): UserContext {
  const next: UserContext = { ...current };

  const budget = parseBudget(text);
  if (budget !== undefined) next.budget = budget;

  const meal = parseMealTime(text);
  if (meal) next.meal_time = meal;

  const people = parsePeople(text);
  if (people !== undefined) next.people = people;

  const loc = parseLocation(text);
  if (loc) {
    next.location = loc;
    next.location_source = "user_message";
  }

  const prefs = parsePreferences(text);
  if (prefs.length) {
    next.preferences = [...new Set([...(current.preferences ?? []), ...prefs])];
  }

  const allergies = parseAllergies(text);
  if (allergies.length) {
    next.allergies = [...new Set([...(current.allergies ?? []), ...allergies])];
  }

  // Ưu tiên parse field vừa được hỏi (vd user trả lời "80k" sau câu hỏi budget)
  if (preferField === "budget" && budget === undefined) {
    const m = text.match(/\d+/);
    if (m) {
      const v = parseInt(m[0], 10);
      next.budget = v < 1000 ? v * 1000 : v;
    }
  }

  return next;
}
