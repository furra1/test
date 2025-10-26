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

async def get_check_history(app):
    """Получить историю всех проверок"""
    service = get_check_service(app)
    history = service.get_all_checks()
    
    # Преобразуем в формат для фронтенда
    history_data = []
    for check in history:
        # Определяем общий статус проверки
        status = check.get('status', 'pending')
        if status == 'completed':
            # Проверяем результаты на ошибки
            has_errors = False
            if 'agent_results' in check:
                has_errors = any(r.get('status') == 'error' for r in check['agent_results'])
            status = 'error' if has_errors else 'success'
        
        history_data.append({
            "id": check.get('id'),
            "target": check.get('target'),
            "date": check.get('created_at', '').strftime('%Y-%m-%d %H:%M') if check.get('created_at') else '',
            "status": status,
            "checks": check.get('checks', [])
        })
    
    # Сортируем по дате (новые первыми)
    history_data.sort(key=lambda x: x['date'], reverse=True)
    
    return {"history": history_data}

async def get_check_stats(app):
    """Получить статистику по проверкам"""
    service = get_check_service(app)
    all_checks = service.get_all_checks()
    
    total = len(all_checks)
    completed = sum(1 for c in all_checks if c.get('status') == 'completed')
    in_progress = sum(1 for c in all_checks if c.get('status') == 'in_progress')
    queued = sum(1 for c in all_checks if c.get('status') == 'queued')
    
    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "queued": queued
    }