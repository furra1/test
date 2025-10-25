// Хранилище для истории проверок
let checkHistory = JSON.parse(localStorage.getItem('checkHistory')) || [];

// Инициализация истории
export function initHistory(historyList, onHistoryItemClick) {
    historyList.innerHTML = '';
    checkHistory.forEach(item => {
        addToHistory(item.target, item.checkId, historyList, onHistoryItemClick);
    });
}

// Добавление в историю
export function addToHistory(target, checkId, historyList, onHistoryItemClick) {
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.innerHTML = `<span class="history-text">${target}</span>`;
    
    historyItem.addEventListener('click', () => {
        onHistoryItemClick(checkId);
    });
    
    historyList.appendChild(historyItem);
    
    // Сохраняем в localStorage
    checkHistory.unshift({ target, checkId });
    if (checkHistory.length > 10) checkHistory = checkHistory.slice(0, 10);
    localStorage.setItem('checkHistory', JSON.stringify(checkHistory));
}