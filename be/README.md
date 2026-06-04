# Food Chat Backend

FastAPI backend — AI gợi ý món ăn & nhà hàng (Anthropic tool-use orchestrator).

## Chạy local

```bash
cd be
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền GEMINI_API_KEY (bắt buộc cho /api/chat)
uvicorn main:app --reload --port 8000
```

## Endpoints

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/health` | Health check |
| POST | `/api/chat` | SSE chat (orchestrator) |
| GET | `/api/restaurants` | Tìm & rank quán (mock nếu không có Places key) |

### POST `/api/chat` (SSE)

Body:

```json
{
  "messages": [{"role": "user", "content": "Trưa một mình 50k không cay"}],
  "context": {
    "location": {"lat": 10.7769, "lng": 106.7009, "address": "Quận 1"},
    "budget": 50000,
    "people": 1,
    "meal_time": "lunch",
    "preferences": [],
    "allergies": []
  }
}
```

SSE events: `thinking`, `food_results`, `restaurant_results`, `ask_context`, `text`, `done`, `error`.

### GET `/api/restaurants`

Query: `lat`, `lng`, `query`, optional `budget`, `radius`, `limit`.

## Log

- File log: `be/logs/app.log` (INFO+) và `be/logs/error.log` (ERROR+)
- Cấu hình: `LOG_DIR`, `LOG_LEVEL` trong `.env`
- Lỗi chi tiết ghi file; user chỉ thấy tin nhắn xin lỗi thân thiện

## Env

| Biến | Mô tả |
|------|--------|
| `GEMINI_API_KEY` | API key từ [Google AI Studio](https://aistudio.google.com/apikey) (bắt buộc cho chat) |
| `GOOGLE_API_KEY` | Alias được chấp nhận thay `GEMINI_API_KEY` |
| `GEMINI_MODEL` | Mặc định `gemini-2.0-flash` |
| `GOOGLE_PLACES_API_KEY` | Tùy chọn |
| `OPENWEATHER_API_KEY` | Tùy chọn |

Xem `.env.example`. Không commit `.env`.
