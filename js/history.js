// API
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';

// Функция для выполнения HTTP-запросов
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        return response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Загрузка истории с сервера
async function loadHistory() {
    try {
        const data = await request('/history');
        return data.history || [];
    } catch (error) {
        console.error('Ошибка загрузки истории:', error);
        // Fallback к демо-данным
        return [];
    }
}

// Отображение истории
function renderHistory(historyData, filter = 'all') {
    const historyList = document.getElementById('historyList');

    // Фильтрация
    const filteredHistory = filter === 'all' ?
        historyData :
        historyData.filter(item => item.status === filter);

    if (filteredHistory.length === 0) {
        historyList.innerHTML = '<div class="empty-history">История проверок пуста</div>';
        return;
    }

    let html = '';
    filteredHistory.forEach(item => {
        const statusClass = `status-${item.status}`;
        const statusText = getStatusText(item.status);

        html += `
            <div class="history-item" data-id="${item.id}">
                <div class="history-target">${item.target}</div>
                <div class="history-date">${item.date}</div>
                <div class="history-status">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="history-actions">
                    <button class="action-btn view-btn" data-id="${item.id}">просмотр</button>
                    <button class="action-btn repeat-btn" data-id="${item.id}">повторить</button>
                </div>
            </div>
        `;
    });

    historyList.innerHTML = html;

    // Добавляем обработчики событий
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.getAttribute('data-id');
            viewCheckDetails(id);
        });
    });

    document.querySelectorAll('.repeat-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.getAttribute('data-id');
            repeatCheck(id);
        });
    });

    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const id = item.getAttribute('data-id');
            viewCheckDetails(id);
        });
    });
}

// Получение текста статуса
function getStatusText(status) {
    switch (status) {
        case 'success':
            return 'Успешно';
        case 'error':
            return 'Ошибка';
        case 'pending':
            return 'В процессе';
        default:
            return 'Неизвестно';
    }
}

// Просмотр деталей проверки
function viewCheckDetails(checkId) {
    alert(`Просмотр деталей проверки: ${checkId}\n\nВ реальном приложении здесь будет открыто модальное окно с детальной информацией.`);
    // В реальном приложении здесь будет переход на страницу с деталями или открытие модального окна
}

// Повтор проверки
function repeatCheck(checkId) {
    alert(`Повтор проверки: ${checkId}\n\nВ реальном приложении здесь будет создана новая проверка с теми же параметрами.`);
    // В реальном приложении здесь будет создание новой проверки с теми же параметрами
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async function() {
    // Загружаем историю с сервера
    const historyData = await loadHistory();

    // Сохраняем в глобальную переменную для фильтрации
    window.currentHistory = historyData;

    // Отображаем историю
    renderHistory(historyData);

    // Добавляем обработчики для фильтров
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Убираем активный класс у всех кнопок
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('active');
            });

            // Добавляем активный класс к текущей кнопке
            this.classList.add('active');

            // Применяем фильтр
            const filter = this.getAttribute('data-filter');
            renderHistory(window.currentHistory, filter);
        });
    });
});