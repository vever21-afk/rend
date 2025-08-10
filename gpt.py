# gpt.py — ключ зашит, без env. Работает сразу.
from openai import OpenAI

# ⚠️ Ключ зашит по твоей просьбе (небезопасно, но сразу работает)
client = OpenAI(api_key="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")

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


