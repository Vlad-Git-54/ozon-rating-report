// Этот скрипт обрабатывает нажатие кнопок на HTML-странице
// и отправляет запрос к REST API /api/report.

document.addEventListener("DOMContentLoaded", () => {
  // Получаем ссылки на элементы DOM
  const btn = document.getElementById("runBtn");
  const minReviewsInput = document.getElementById("minReviews");
  const sendToTelegramInput = document.getElementById("sendToTelegram");
  const result = document.getElementById("result");

  // Вешаем обработчик на кнопку
  btn.addEventListener("click", async () => {
    // Считываем значение минимального количества отзывов
    const minReviews = parseInt(minReviewsInput.value || "0", 10);
    // Считываем флаг отправки в Telegram
    const sendToTelegram = sendToTelegramInput.checked;

    // Оповещение о начале формирования отчета
    result.textContent = "Формируем отчёт...";

    try {
      // Отправляем POST-запрос к эндпоинту /api/report
      const response = await fetch("/api/report", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          min_reviews: minReviews,
          send_to_telegram: sendToTelegram
        })
      });

      // Обработка неуспешного ответа (код не 2xx)
      if (!response.ok) {
        const text = await response.text();
        result.textContent = "Ошибка: " + response.status + " " + text;
        return;
      }

      // Читаем JSON-ответ
      const data = await response.json();
      result.textContent =
        "Отчёт сформирован.\nФайл: " + data.file_path + "\nСтрок в отчёте: " + data.rows;
    } catch (e) {
      // Обработка сетевых ошибок
      result.textContent = "Ошибка запроса: " + e;
    }
  });
});
