""" Модуль с логикой формирования Excel-отчёта."""

# Использует OzonClient для получения данных из Seller API,
# pandas для обработки и сохранения в Excel


import os                       # работа с путями и каталогами
from datetime import datetime   # для создания метки времени в имени файла

import pandas as pd             # библиотека для работы с табличными данными

from app.config import settings     # путь к отчётам
from app.ozon_client import OzonClient  # фасад к Seller API


def generate_report(min_reviews: int = 0) -> str:

    # min_reviews — минимальное количество отзывов, чтобы товар был включён в отчёт.

    # Убеждаемся, что каталог отчётов существует
    os.makedirs(settings.report_dir, exist_ok=True)

    # Создаём клиента для работы с Seller API
    client = OzonClient()

    # Сопоставление sku → offer_id, name
    sku_map = client.get_sku_map()

    # Статистика отзывов: sku → sum, cnt, last
    reviews_stat = client.get_reviews_stat()

    rows: list[dict] = []

    for sku, info in sku_map.items():
        stat = reviews_stat.get(sku)

        if stat:
            avg_rating = round(stat["sum"] / stat["cnt"], 2)
            count = stat["cnt"]
            last_date = stat["last"]
        else:
            avg_rating = None
            count = 0
            last_date = ""

        # Фильтрация по минимальному количеству отзывов
        if count < min_reviews:
            continue

        rows.append({
            "SKU": sku,
            "Offer ID": info["offer_id"],
            "Наименование товара": info["name"],
            "Средний рейтинг": avg_rating,
            "Количество отзывов": count,
            "Последний отзыв": last_date,
        })

    # Создаём DataFrame из списка словарей
    df = pd.DataFrame(rows)

    # Формируем имя файла с текущей датой и временем
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    file_path = os.path.join(settings.report_dir, f"ozon_report_{ts}.xlsx")

    # Сохраняем таблицу в Excel
    df.to_excel(file_path, index=False)

    print("Отчёт сохранён в файл:", file_path)
    print("Количество строк в отчёте:", len(df))

    return file_path
