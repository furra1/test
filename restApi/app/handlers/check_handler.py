from app.services.checks_service import CheckService

def get_check_service(app) -> CheckService:
    """Получить или создать экземпляр CheckService из контекста app"""
    if 'check_service' not in app:
        app['check_service'] = CheckService()
    return app['check_service']

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
    service = get_check_service(app)
    check_id = await service.create_check(target, checks)
    
    return {
        "checkId": check_id,
        "status": "queued",
        "target": target,
        "checks": checks
    }

async def get_check_result(check_id: str, app):
    """Получить результат проверки по ID"""
    service = get_check_service(app)
    result = service.get_check_by_id(check_id)
    
    if not result:
        return {
            "error": f"Проверка {check_id} не найдена",
            "status": "not_found"
        }
    
    return result