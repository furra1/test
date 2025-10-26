// Глобальная конфигурация API
// Переопределяется из window.API_BASE_URL если установлено
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';

// Функция для установки API URL (используется при деплое)
window.setApiBaseUrl = function(url) {
    window.API_BASE_URL = url;
};