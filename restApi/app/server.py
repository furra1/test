from aiohttp import web
from app.routes.checks import checks_routes
from app.routes.agents import agent_routes
import logging

logger = logging.getLogger(__name__)

# Белый список разрешенных доменов
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
]

# Middleware для CORS
@web.middleware
async def cors_middleware(request, handler):
    origin = request.headers.get('Origin', '')
    
    # Обработка preflight запросов
    if request.method == 'OPTIONS':
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # Обрабатываем обычные запросы
    response = await handler(request)
    
    # Добавляем CORS заголовки
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    # Безопасные заголовки
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

# Middleware для валидации JSON
@web.middleware
async def validate_json_middleware(request, handler):
    # Логируем запрос
    logger.info(f"{request.method} {request.path} - IP: {request.remote}")
    
    if request.content_type == 'application/json':
        try:
            # Читаем тело запроса
            body = await request.read()
            
            # Ограничение размера (1 MB)
            if len(body) > 1024 * 1024:
                raise web.HTTPRequestEntityTooLarge()
            
            # Парсим JSON
            import json
            request._json_data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            raise web.HTTPBadRequest(reason="Invalid JSON")
    
    return await handler(request)

# Middleware для обработки ошибок
@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as e:
        # Логируем ошибки
        logger.error(f"HTTP {e.status}: {e.reason} - {request.method} {request.path}")
        raise
    except Exception as e:
        # Не раскрываем внутренние ошибки
        logger.error(f"Internal error: {str(e)} - {request.method} {request.path}")
        raise web.HTTPInternalServerError()

# Middleware для rate limiting (простая реализация)
from collections import defaultdict
from datetime import datetime

request_counts = defaultdict(int)
last_reset = datetime.now()

@web.middleware
async def rate_limit_middleware(request, handler):
    global last_reset
    ip = request.remote
    
    # Сброс счетчика раз в минуту
    if (datetime.now() - last_reset).total_seconds() > 60:
        request_counts.clear()
        last_reset = datetime.now()
    
    # Лимит: 100 запросов в минуту с одного IP
    if request_counts[ip] > 100:
        raise web.HTTPTooManyRequests(reason="Rate limit exceeded")
    
    request_counts[ip] += 1
    return await handler(request)

def create_app():
    app = web.Application()
    
    # Подключаем middleware в правильном порядке
    app.middlewares.append(error_middleware)
    app.middlewares.append(rate_limit_middleware)
    app.middlewares.append(validate_json_middleware)
    app.middlewares.append(cors_middleware)
    
    app.add_routes(checks_routes)
    app.add_routes(agent_routes)
    
    return app
    