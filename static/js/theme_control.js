document.addEventListener('DOMContentLoaded', function() {
    // Проверяем сохраненную тему в localStorage
    const savedTheme = localStorage.getItem('daisyui-theme') || 'default';


    // Находим соответствующий radio-элемент и отмечаем его
    const radioToCheck = document.querySelector(`input[value="${savedTheme}"]`);
    if (radioToCheck) {
      radioToCheck.checked = true;
    }

    // Обработчик изменения темы
    document.querySelectorAll('.theme-controller').forEach(radio => {
      radio.addEventListener('change', function() {
        const selectedTheme = this.value;
        document.documentElement.setAttribute('data-theme', selectedTheme);
        localStorage.setItem('daisyui-theme', selectedTheme);
      });
    });
  });