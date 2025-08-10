import os
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai

# === Конфигурация ===
TELEGRAM_TOKEN = "8377982156:AAFPAx2X5tbeXxtsZ4oxS7Y8uE9o6-e6G9g"
OPENAI_API_KEY = "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"
WEBHOOK_SECRET = "my_secret_webhook"
BASE_URL = "https://telegram-bot-1hu8.onrender.com"

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# === Установка вебхука ===
def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    webhook_url = f"{BASE_URL}/webhook/{WEBHOOK_SECRET}"
    resp = requests.post(url, json={"url": webhook_url})
    logging.info(f"Webhook set response: {resp.text}")

@app.on_event("startup")
def startup_event():
    set_webhook()

# === Обработка входящих сообщений ===
@app.post(f"/webhook/{{secret}}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    data = await request.json()
    logging.info(f"Incoming update: {data}")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]

        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_text}
                ]
            )
            answer = gpt_response.choices[0].message["content"]
        except Exception as e:
            answer = f"Ошибка GPT: {e}"

        send_message(chat_id, answer)

    return JSONResponse(status_code=200, content={"ok": True})

# === Функция отправки сообщений в Telegram ===
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.get("/")
def root():
    return {"status": "Bot is running!"}
