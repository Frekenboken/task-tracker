function updateClockHand() {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();

  // Рассчитываем угол (0° = 12:00, 360° = 24:00)
  const angle = (hours % 24) * 15 + minutes * 0.25;

  // Применяем поворот к элементу с id="hand"
  const hand = document.getElementById("hand");
  if (hand) {
    hand.style.transform = `rotate(${angle}deg)`;
  }
}

// Запускаем обновление каждую минуту (60 000 мс)
setInterval(updateClockHand, 60000);

// Первый вызов сразу (чтобы не ждать минуту)
updateClockHand();