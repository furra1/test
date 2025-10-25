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