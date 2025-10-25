import { api } from './api.js';

// Показать секцию с результатами и установить ID проверки
export function showResultsSection(checkId, checkIdSpan, resultsSection, resultsContainer) {
    checkIdSpan.textContent = `ID проверки: ${checkId}`;
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '<p>Проверка запущена, ожидаем результаты...</p>';
    
    // Прокручиваем страницу к результатам
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Рендерим результаты на странице
export function renderResults(data, resultsContainer) {
    if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = '<p>Результаты пока не доступны...</p>';
        return;
    }

    let html = '';

    data.results.forEach(agentResult => {
        const statusClass = getStatusClass(agentResult.status);
        const statusText = getStatusText(agentResult.status);

        html += `
            <div class="agent-result">
                <h4>Агент: ${agentResult.agent_id || 'Unknown'} 
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </h4>
                ${agentResult.log ? `<div class="log-entry">${escapeHtml(agentResult.log)}</div>` : ''}
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}

// Функция для опроса результатов проверки
export async function pollCheckResults(checkId, resultsContainer) {
    const maxAttempts = 30;
    const interval = 2000;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            console.log(`Опрос результатов, попытка ${attempt + 1}`);
            const result = await api.getCheckResult(checkId);
            renderResults(result, resultsContainer);
            
            // Если все проверки завершены, прекращаем опрос
            if (isCheckComplete(result)) {
                console.log('Проверка завершена');
                break;
            }
            
            // Ждём перед следующим запросом
            await new Promise(resolve => setTimeout(resolve, interval));
            
        } catch (error) {
            console.error('Ошибка при получении результатов:', error);
            resultsContainer.innerHTML = `<p class="status-error">Ошибка: ${error.message}</p>`;
            break;
        }
    }
}

// Проверяем, все ли проверки завершены
function isCheckComplete(result) {
    if (!result.results) return false;
    return result.results.every(agentResult => 
        agentResult.status === 'completed' || agentResult.status === 'error'
    );
}

// Вспомогательные функции
function getStatusClass(status) {
    switch (status) {
        case 'completed': return 'status-success';
        case 'error': return 'status-error';
        case 'pending': 
        default: return 'status-pending';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'completed': return 'Завершено';
        case 'error': return 'Ошибка';
        case 'pending': 
        default: return 'В процессе';
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}