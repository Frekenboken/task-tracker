const calendar = document.getElementById("calendar");
pageDate = window.location.href.split('/').pop();
calendar.value = pageDate


calendar.addEventListener('change', (e) => {
  const selectedDate = calendar.value; // Получаем выбранную дату
  const redirectUrl = "/home/" + selectedDate;
  if (pageDate != selectedDate) {
    window.location.href = redirectUrl; // Редирект
  }
});