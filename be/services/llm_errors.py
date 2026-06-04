def is_llm_unavailable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    markers = (
        "gemini_api_key",
        "google_api_key",
        "is not set",
        "429",
        "resource_exhausted",
        "quota",
        "invalid api key",
        "api key not valid",
        "permission denied",
        "401",
        "403",
        "invalid_argument",
        "thought_signature",
    )
    return any(m in msg for m in markers)


def friendly_message(exc: BaseException) -> str:
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        return (
            "Gemini hết quota / free tier (429). "
            "Đổi GEMINI_MODEL, bật billing, hoặc tạo key mới tại https://aistudio.google.com/apikey. "
            "Hệ thống đã chuyển sang chế độ gợi ý dự phòng."
        )
    if "not set" in msg.lower():
        return "Chưa cấu hình GEMINI_API_KEY trong be/.env"
    return f"Lỗi AI: {msg[:300]}"
