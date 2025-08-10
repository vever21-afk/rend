
import os
import logging
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, Request, HTTPException
import uvicorn

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

from gpt import call_gpt, transcribe_audio

logging.basicConfig(level=logging.INFO)

# === Config (embedded, per user request) ===
BOT_TOKEN = "8377982156:AAFPAx2X5tbeXxtsZ4oxS7Y8uE9o6-e6G9g"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret-path-123")  # can override in Render
# ===========================================

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Simple menu handlers ---
@dp.message(CommandStart())
async def start(m: Message):
    await m.answer("Привет! Я на вебхуках и работаю бесплатно на Render. Напиши текст или пришли voice.")

@dp.message(F.voice)
async def handle_voice(m: Message):
    tmp = NamedTemporaryFile(delete=False, suffix=".ogg")
    await m.bot.download(m.voice.file_id, tmp)
    tmp.close()
    try:
        text = await transcribe_audio(tmp.name)
        reply = await call_gpt([{"role":"user","content": text}])
        await m.answer(f"🗣️ Распознал: «{text}»\n\n{reply}", parse_mode=ParseMode.HTML)
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

@dp.message()
async def dialog(m: Message):
    reply = await call_gpt([{"role":"user","content": m.text or ""}])
    await m.answer(reply, parse_mode=ParseMode.HTML)

# --- FastAPI app & webhook route ---
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Render exposes public URL in RENDER_EXTERNAL_URL
    base_url = os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        logging.warning("RENDER_EXTERNAL_URL not set. Using local dev url.")
        base_url = "https://example.com"
    webhook_url = f"{base_url}/webhook/{WEBHOOK_SECRET}"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logging.info(f"Webhook set to: {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

@app.post("/webhook/{WEBHOOK_SECRET}")
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}

# Healthcheck endpoint (Render pings it)
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
