# gpt.py — только ENV, без хардкода
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # так увидим причину в логах Render, не паля ключ
    raise RuntimeError("OPENAI_API_KEY is not set in environment")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = (
    "You are a warm, concise CBT/ACT-based mental well-being assistant. "
    "Never diagnose; avoid promises to 'cure'. Always suggest one 5-minute actionable step. "
    "If user mentions self-harm or suicidal intent, stop and show a safety protocol."
)

async def call_gpt(messages: list[dict]) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка GPT: {e}"

async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            tr = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                temperature=0
            )
        return tr.strip()
    except Exception as e:
        return f"Ошибка распознавания: {e}"

