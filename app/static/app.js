// Этот скрипт отвечает за взаимодействие HTML-страницы с нашим REST API.

/**
 * Функция инициализации интерфейса.
 * Вызывается, когда DOM загружен.
 */
document.addEventListener("DOMContentLoaded", () => {
  // Находим элементы формы по их id
  const runBtn = document.getElementById("runBtn");
  const minReviewsInput = document.getElementById("minReviews");
  const resultEl = document.getElementById("result");

  // Навешиваем обработчик события "click" на кнопку
  runBtn.addEventListener("click", async () => {
    // Считываем значение минимального количества отзывов из поля ввода
    const minReviews = parseInt(minReviewsInput.value || "0", 10);

    // Сообщаем пользователю, что процесс начался
    resultEl.textContent = "Формируем отчёт...";

    try {
      // Отправляем POST-запрос на эндпоинт /api/report нашего FastAPI-приложения
      const response = await fetch("/api/report", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({min_reviews: minReviews})
      });

      // Если статус ответа не 2xx — показываем ошибку
      if (!response.ok) {
        const text = await response.text();
        resultEl.textContent = "Ошибка: " + response.status + " " + text;
        return;
      }

      // Если всё хорошо — читаем JSON-ответ
      const data = await response.json();

      // Выводим пользователю путь к файлу и количество строк
      resultEl.textContent =
        "Отчёт сформирован.\nФайл: " + data.file_path + "\nСтрок в отчёте: " + data.rows;
    } catch (e) {
      // Обрабатываем возможные сетевые ошибки
      resultEl.textContent = "Ошибка запроса: " + e;
    }
  });
});
