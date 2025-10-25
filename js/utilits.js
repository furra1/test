// Утилиты для работы с DOM и анимациями
export function setupButtonAnimations() {
    const checkButton = document.querySelector('.check-button');
    
    checkButton.addEventListener('mouseenter', function() {
        if (!this.disabled) {
            this.style.transform = 'translateY(-2px)';
        }
    });
    
    checkButton.addEventListener('mouseleave', function() {
        if (!this.disabled) {
            this.style.transform = 'translateY(0)';
        }
    });
}

// Валидация формы
export function validateForm(target, selectedChecks) {
    if (!target || selectedChecks.length === 0) {
        alert('Пожалуйста, заполните хост и выберите хотя бы один тип проверки.');
        return false;
    }
    return true;
}

// Управление состоянием кнопки
export function setButtonState(button, isDisabled, text = 'проверить') {
    button.disabled = isDisabled;
    button.textContent = text;
}