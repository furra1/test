# Политика безопасности REST API

## Реализовано ✅

1. **CORS с белым списком** - Только разрешенные домены могут обращаться к API
2. **Rate Limiting** - 100 запросов в минуту с IP
3. **Валидация JSON** - Проверка размера (1 MB) и формата
4. **Защитные заголовки** - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
5. **Логирование** - Все запросы и ошибки логируются
6. **Обработка ошибок** - Нет раскрытия внутренних деталей

## Рекомендации для продакшена 🚀

### 1. HTTPS обязателен
```python
# Используйте SSL/TLS
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('server.crt', 'server.key')

web.run_app(app, port=8443, ssl_context=context)
```

### 2. Аутентификация (JWT)
```python
from jose import jwt

SECRET_KEY = "your-secret-key"

def create_token(user_id):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### 3. Валидация входных данных
```python
import validators

def validate_target(target):
    if not validators.url(target):
        raise ValueError("Invalid URL")
    if not target.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return target
```

### 4. SQL Injection защита
```python
# ✅ ПРАВИЛЬНО - параметризованные запросы
cur.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))

# ❌ НЕПРАВИЛЬНО - строковая конкатенация
cur.execute(f"SELECT * FROM agents WHERE id = {agent_id}")
```

### 5. Хранилище секретов
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает .env файл

SECRET_KEY = os.getenv('SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

### 6. Rate Limiting (Redis)
```python
import redis
import aioredis

async def rate_limit(ip, limit=100, window=60):
    redis_client = await aioredis.create_redis_pool()
    key = f"rate_limit:{ip}"
    current = await redis_client.get(key)
    
    if current and int(current) > limit:
        raise web.HTTPTooManyRequests()
    
    await redis_client.incr(key)
    await redis_client.expire(key, window)
```

### 7. Мониторинг и алерты
- Настройте логирование в файл
- Интегрируйте Sentry для отслеживания ошибок
- Используйте Prometheus для метрик

### 8. Backup базы данных
```bash
# Регулярные бэкапы SQLite
sqlite3 agents.db ".backup backup.db"
```

### 9. Зависимости
```bash
# Регулярно проверяйте уязвимости
pip install pip-audit
pip-audit
```

### 10. Документация
- Используйте OpenAPI/Swagger для документирования API
- Включите примеры запросов/ответов
- Описывайте коды ошибок

## Чек-лист перед деплоем

- [ ] HTTPS включен
- [ ] Аутентификация реализована
- [ ] Все секреты в .env (не в коде)
- [ ] Rate limiting настроен
- [ ] Валидация входных данных
- [ ] SQL injection защита
- [ ] Логирование настроено
- [ ] CORS настроен правильно
- [ ] Зависимости обновлены
- [ ] Тесты написаны
- [ ] Backup настроен
- [ ] Мониторинг настроен

## Контакты для уязвимостей

Если найдете уязвимость - пишите на security@example.com
