const API_BASE_URL = 'http://localhost:8000/api';

// Функция для выполнения HTTP-запросов с обработкой ошибок
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
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        console.error('Request failed:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.');
        }
        throw error;
    }
}

// API методы
export const api = {
    // Создать новую проверку
    async createCheck(checkData) {
        return request('/check', {
            method: 'POST',
            body: JSON.stringify(checkData),
        });
    },

    // Получить результат проверки по ID
    async getCheckResult(checkId) {
        return request(`/check/${checkId}`);
    },

    // Получить список агентов (для будущей страницы статуса)
    async getAgents() {
        return request('/agents');
    },
};