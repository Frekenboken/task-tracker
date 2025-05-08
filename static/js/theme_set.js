// Проверяем сохраненную тему в localStorage
const savedTheme = localStorage.getItem('daisyui-theme') || 'default';

// Устанавливаем сохраненную тему
document.documentElement.setAttribute('data-theme', savedTheme);
