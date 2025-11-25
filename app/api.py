""" HTTP API и HTML UI проекта. """

# Используем FastAPI для реализации REST API
# GET /api/health - проверка работоспособности сервера
# POST /api/report - генерация отчёта



from __future__ import annotations

import os                          # работа с путями к файлам

from fastapi import FastAPI        # основной класс FastAPI-приложения
from fastapi.staticfiles import StaticFiles  # раздача статики (HTML, JS, CSS)
from fastapi.responses import FileResponse   # возвращает index.html
from pydantic import BaseModel, Field        # описание схем входных/выходных данных

import pandas as pd                # чтобы посчитать количество строк в отчёте

from app.report import generate_report  # функция формирования отчёта


# Создаём экземпляр FastAPI-приложения
app = FastAPI(title="Ozon Rating Report API")

# Определяем путь к статическим файлам (app/static)
BASE_DIR = os.path.dirname(__file__)             # путь до папки app
STATIC_DIR = os.path.join(BASE_DIR, "static")    # app/static

# Монтируем статику по URL /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ReportParams(BaseModel):
    """Входные параметры для API /api/report."""
  
    min_reviews: int = Field(0, ge=0, description="Минимальное количество отзывов")


class ReportResponse(BaseModel):
    """Модель ответа API /api/report."""
  
    file_path: str
    rows: int


@app.get("/api/health")
def health() -> dict:
    """Проверка сервера."""
  
    return {"status": "ok"}


@app.post("/api/report", response_model=ReportResponse)
def api_report(params: ReportParams) -> ReportResponse:
    """Генерация отчёта."""
  
    file_path = generate_report(min_reviews=params.min_reviews)
    df = pd.read_excel(file_path)
    return ReportResponse(file_path=file_path, rows=len(df))


@app.get("/")
def index() -> FileResponse:
    """Корень сайта ("/")"""
  
    html_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(html_path)
  
