import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.logging_config import get_logger, log_exception, setup_logging
from routers import chat, restaurants

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)
setup_logging()

logger = get_logger("main")

app = FastAPI(title="Food Chat API", version="1.0.0")

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed = [o.strip() for o in _origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(restaurants.router, prefix="/api", tags=["restaurants"])


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_exception(logger, f"Unhandled {request.method} {request.url.path}", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Xin lỗi, hệ thống gặp sự cố. Vui lòng thử lại sau.",
        },
    )


@app.get("/api/health")
async def health():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    llm_ok = bool(key) and not key.startswith("AQ.")
    log_dir = Path(os.getenv("LOG_DIR", str(Path(__file__).resolve().parent / "logs")))
    return {
        "status": "ok",
        "version": "1.0.0",
        "llm_configured": bool(key),
        "llm_key_format_ok": llm_ok,
        "llm_model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
        "fallback_available": True,
        "log_dir": str(log_dir),
    }
