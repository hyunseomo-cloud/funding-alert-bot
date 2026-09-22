import os

import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def send_telegram_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        TELEGRAM_API.format(token=token, method="sendMessage"),
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"Telegram API HTTP {resp.status_code}: {resp.text[:500]}")


def get_updates(offset: int, timeout: int = 0) -> list:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    resp = requests.get(
        TELEGRAM_API.format(token=token, method="getUpdates"),
        params={"offset": offset, "timeout": timeout},
        timeout=timeout + 15,
    )
    if not resp.ok:
        raise RuntimeError(f"Telegram API HTTP {resp.status_code}: {resp.text[:500]}")
    return resp.json().get("result", [])
