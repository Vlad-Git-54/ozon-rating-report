""" Простой тест для функции generate_report() """

import os                                   # проверка наличия файла
from app.report import generate_report      # функция формирования отчёта
from app.config import settings             # настройки (report_dir)


def test_generate_report_creates_file(tmp_path, monkeypatch):

    # 1. Перенаправляем каталог report_dir во временную папку (tmp_path)
    # 2. Вызываем generate_report()
    # 3. Проверяем, что файл создан и имеет расширение .xlsx
    
    # Подменяем путь к каталогу отчётов на временный
    monkeypatch.setattr(settings, "report_dir", str(tmp_path))

    # Формируем отчёт
    file_path = generate_report(min_reviews=0)

    # Проверяем существование файла
    assert os.path.exists(file_path)
    # Проверяем, что это Excel-файл
    assert file_path.endswith(".xlsx")
