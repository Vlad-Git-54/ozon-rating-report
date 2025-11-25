# Модуль конфигурации проекта. Используем Pydantic BaseSettings для загрузки настроек из .env 

from pydantic import BaseSettings  # базовый класс для описания настроек
from pydantic import Field        # позволяет задать доп. параметры

class Settings(BaseSettings):
    """Класс настроек приложения. Значения будут автоматически прочитаны из файла .env"""

    # Идентификатор клиента Seller API (из личного кабинета Ozon)
    ozon_client_id: str = Field(..., env="OZON_CLIENT_ID", description="Client-Id для Seller API")

    # API-ключ Seller API (из личного кабинета Ozon)
    ozon_api_key: str = Field(..., env="OZON_API_KEY", description="Api-Key для Seller API")

    # Каталог, где будут сохраняться Excel-отчёты
    report_dir: str = Field("reports", description="Каталог для сохранения Excel-отчётов")

    class Config:
        # Имя файла с переменными окружения
        env_file = ".env"
        # Кодировка файла .env
        env_file_encoding = "utf-8"


# Создаём единственный экземпляр настроек.
settings = Settings()
