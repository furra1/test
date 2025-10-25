import { api } from './api.js';
import { initHistory, addToHistory } from './history.js';
import { showResultsSection, pollCheckResults, renderResults } from './ui.js';
import { setupButtonAnimations, validateForm, setButtonState } from './utils.js';

// Получаем элементы DOM
const checkForm = document.getElementById('checkForm');
const targetInput = document.getElementById('target');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const checkIdSpan = document.getElementById('checkId');
const historyList = document.getElementById('historyList');

// Колбэк для клика по истории
function onHistoryItemClick(checkId) {
    showResultsSection(checkId, checkIdSpan, resultsSection, resultsContainer);
    pollCheckResults(checkId, resultsContainer);
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    initHistory(historyList, onHistoryItemClick);
    setupButtonAnimations();
});

// Обработчик отправки формы
checkForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Получаем данные из формы
    const target = targetInput.value.trim();
    const checkboxes = document.querySelectorAll('input[name="checks"]:checked');
    const selectedChecks = Array.from(checkboxes).map(cb => cb.value);

    if (!validateForm(target, selectedChecks)) {
        return;
    }

    // Блокируем кнопку на время отправки
    setButtonState(submitBtn, true, 'проверка...');

    try {
        console.log('Отправка запроса на бэкенд...');
        
        // Отправляем запрос на бэкенд
        const checkData = {
            target,
            checks: selectedChecks,
        };

        const result = await api.createCheck(checkData);
        console.log('Ответ от бэкенда:', result);
        
        // Добавляем в историю
        addToHistory(target, result.checkId, historyList, onHistoryItemClick);
        
        // Показываем секцию с результатами
        showResultsSection(result.checkId, checkIdSpan, resultsSection, resultsContainer);
        
        // Начинаем опрашивать бэкенд для получения результатов
        pollCheckResults(result.checkId, resultsContainer);

    } catch (error) {
        console.error('Ошибка при создании проверки:', error);
        alert(`Ошибка: ${error.message}\n\nУбедитесь, что:\n1. Бэкенд запущен на localhost:8000\nn2. CORS настроен правильно`);
    } finally {
        // Разблокируем кнопку
        setButtonState(submitBtn, false, 'проверить');
    }
});