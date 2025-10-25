from app.services.checks_service import CheckService

# Глобальный экземпляр сервиса (singleton)
_check_service = None

def get_check_service() -> CheckService:
    """Получить или создать экземпляр CheckService"""
    global _check_service
    if _check_service is None:
        _check_service = CheckService()
    return _check_service

async def create_check(data, app):
    """Создать новую проверку"""
    target = data.get('target')
    checks = data.get('checks', [])
    
    # Валидация
    if not target:
        raise ValueError("Не указан target")
    
    if not checks or len(checks) == 0:
        raise ValueError("Не указаны типы проверок")
    
    # Создаем проверку через сервис
    service = get_check_service()
    check_id = await service.create_check(target, checks)
    
    return {
        "checkId": check_id,
        "status": "queued",
        "target": target,
        "checks": checks
    }

async def get_check_result(check_id: str, app):
    """Получить результат проверки по ID"""
    service = get_check_service()
    result = service.get_check_by_id(check_id)
    
    if not result:
        return {
            "error": f"Проверка {check_id} не найдена",
            "status": "not_found"
        }
    
    return result