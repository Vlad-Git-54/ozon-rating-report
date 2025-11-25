from __future__ import annotations

import requests             # HTTP-запрос к Telegram Bot API

from app.config import settings  # настройки (tg_token, tg_chat_id)


class TelegramClient:
    def __init__(self) -> None:
        self.token = settings.tg_token
        self.chat_id = settings.tg_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_document(self, file_path: str, caption: str | None = None) -> None:
        url = f"{self.base_url}/sendDocument"
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": self.chat_id}
            if caption:
                data["caption"] = caption
            response = requests.post(url, data=data, files=files, timeout=60)

        if response.status_code != 200:
            print("Ошибка отправки в Telegram:", response.status_code, response.text)
        else:
            print("Отчёт отправлен в Telegram:", file_path)
