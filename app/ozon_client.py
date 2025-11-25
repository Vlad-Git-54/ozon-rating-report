# Модуль клиента для Ozon Seller API. Реализуем паттерн Facade:
# Скрываем детали HTTP-запросов,
# Предоставляем простые методы get_sku_map(), get_reviews_stat().

from __future__ import annotations  # позволяет использовать аннотации типов в виде строк (для совместимости)

import time                         # пауза между запросами, чтобы не упираться в лимиты OZON Seller API
from typing import Dict, List       # типы словарь и список для аннотаций

import requests                     # библиотека для HTTP-запросов

from app.config import settings     # импорт конфига (client_id, api_key)


class OzonClient:
    """ Класс-фасад для Seller API. """

    def __init__(self) -> None:
      
        # Сохраняет базовый URL и ключи доступа
      
        self.base_url = "https://api-seller.ozon.ru"
        self.client_id = settings.ozon_client_id
        self.api_key = settings.ozon_api_key

    def _post(self, path: str, payload: dict | None = None) -> dict:
        
        # Внутренний метод отправки POST-запроса
        # path    - путь (например "/v3/product/list")
        # payload - тело запроса в виде словаря 
        
        url = f"{self.base_url}{path}"
        headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        response = requests.post(url, json=payload or {}, headers=headers, timeout=60)

        # Для отладки печатаем ошибку, если статус не 200
        if response.status_code != 200:
            print(path, "→", response.status_code, response.text[:200])

        # Если статус не 200, выбрасывает исключение
        response.raise_for_status()

        # Возвращаем JSON-ответ в виде словаря
        return response.json()


   """ Работа с товарами (каталог) """

    def get_all_product_ids(self) -> List[int]:
       
        # Получить список всех product_id магазина

        # Используем метод /v3/product/list с пагинацией
    
        product_ids: List[int] = []
        last_id = ""

        while True:
            data = self._post(
                "/v3/product/list",
                {
                    "filter": {"visibility": "ALL"},  # все видимые товары
                    "limit": 1000,                    # максимум 1000 за раз
                    "last_id": last_id,               # курсор пагинации
                },
            )
            items = data.get("result", {}).get("items", [])
            if not items:
                break

            # Сохраняем product_id
            product_ids.extend(item["product_id"] for item in items)

            # Обновляем курсор
            last_id = data["result"].get("last_id")
            if not last_id:
                break

        return product_ids

    def get_sku_map(self) -> Dict[int, Dict]:
        
        # 1. Получаем все product_id
        # 2. Вызываем /v3/product/info/list по 50 запросов за раз
        # 3. Из ответа берём sku, offer_id и name

        product_ids = self.get_all_product_ids()
        print(f"Найдено товаров: {len(product_ids)}")

        sku_map: Dict[int, Dict] = {}

        for start in range(0, len(product_ids), 50):
            batch_ids = product_ids[start:start + 50]
            data = self._post(
                "/v3/product/info/list",
                {
                    "product_id_type": "PRODUCT_ID",
                    "product_id": batch_ids,
                },
            )
            # Список товаров в ответе лежит в ключе "items"
            items = data.get("items", [])
            print(f"  info batch {start}-{start+len(batch_ids)}: {len(items)} записей")

            for it in items:
                sku = it.get("sku")
                if not sku:
                    continue
                sku_map[sku] = {
                    "offer_id": it.get("offer_id"),
                    "name": it.get("name"),
                }

        print("Всего SKU в каталоге:", len(sku_map))
        return sku_map

    
    """ Работа с отзывами """


    def get_reviews_stat(self) -> Dict[int, Dict]:

        # Использует метод /v1/review/list с пагинацией
        # Формируем словарь:
        #    stat[sku] = {
        #        "sum":  сумма оценок,
        #        "cnt":  количество отзывов,
        #        "last": дата последнего отзыва,
        #  }

        reviews_stat: Dict[int, Dict] = {}
        last_id = ""
        total = 0

        while True:
            data = self._post("/v1/review/list", {"limit": 100, "last_id": last_id})
            reviews = data.get("reviews", [])
            if not reviews:
                break

            for rv in reviews:
                sku = rv.get("sku")
                rating = rv.get("rating")
                published = rv.get("published_at") or rv.get("date") or rv.get("created_at")

                if sku is None or rating is None:
                    continue

                stat = reviews_stat.setdefault(sku, {"sum": 0, "cnt": 0, "last": None})
                stat["sum"] += rating
                stat["cnt"] += 1

                if published and (stat["last"] is None or published > stat["last"]):
                    stat["last"] = published

            total += len(reviews)
            print("Прочитано отзывов:", total)

            if not data.get("has_next"):
                break

            last_id = data.get("last_id")
            if not last_id:
                break

            # Пауза, чтобы соблюдать лимиты по количеству запросов
            time.sleep(0.2)

        print("SKU с найденными отзывами:", len(reviews_stat))
        return reviews_stat
