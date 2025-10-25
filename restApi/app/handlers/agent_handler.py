from agent_database import agent_db

# Глобальный экземпляр базы данных
_db = None

def get_db():
    """Получить или создать экземпляр базы данных"""
    global _db
    if _db is None:
        _db = agent_db()
    return _db

async def get_agents(app):
    """Получить список агентов"""
    db = get_db()
    agents = db.get_all_agents()
    return {"agents": agents}

async def update_heartbeat(data, app):
    """Обновить heartbeat агента"""
    db = get_db()
    agent_id = data.get('agent_id')
    token = data.get('token')
    
    if not agent_id and not token:
        raise ValueError("Не указан agent_id или token")
    
    if token:
        # Найти агента по токену
        agent = db.get_agent_by_token(token)
        if not agent:
            raise ValueError("Агент с таким токеном не найден")
        agent_id = agent['id']
    
    db.update_heartbeat(agent_id)
    return {"status": "updated", "agent_id": agent_id}

async def create_agent(data, app):
    """Создать нового агента"""
    db = get_db()
    
    name = data.get('name')
    location = data.get('location')
    ip = data.get('ip')
    token = data.get('token')
    
    if not all([name, location, ip, token]):
        raise ValueError("Не указаны все обязательные поля")
    
    agent_id = db.create_agent(name, location, ip, token)
    return {"agent_id": agent_id, "status": "created"}

async def get_agent_tasks(app):
    """Получить задачи для агентов"""
    # Получаем задачи из сервиса проверок
    from app.services.checks_service import CheckService
    
    # Создаем временный сервис для получения задач
    service = CheckService()
    checks = service.get_all_checks()
    
    # Фильтруем задачи, которые еще не выполнены
    pending_tasks = []
    for check in checks:
        if check.get('status') == 'queued':
            for check_type in check.get('checks', []):
                pending_tasks.append({
                    'id': f"{check['id']}_{check_type}",
                    'check_id': check['id'],
                    'type': check_type,
                    'target': check['target']
                })
    
    return {"tasks": pending_tasks}

async def send_agent_results(data, app):
    """Обработать результаты от агента"""
    task_id = data.get('task_id')
    agent_id = data.get('agent_id')
    results = data.get('results')
    
    if not all([task_id, agent_id, results]):
        raise ValueError("Не указаны все обязательные поля")
    
    # Здесь можно добавить логику обработки результатов
    # Например, обновление статуса задачи в базе данных
    
    return {"status": "received", "task_id": task_id}
