from aiohttp import web
from app.handlers.agent_handler import get_agents, update_heartbeat, create_agent, get_agent_tasks, send_agent_results

agent_routes = web.RouteTableDef()

@agent_routes.options('/api/agents')
async def options_agents_handler(request):
    """Обработка preflight запросов для CORS"""
    return web.Response()

@agent_routes.get('/api/agents')
async def get_agents_handler(request):
    """Получить список агентов"""
    try:
        result = await get_agents(request.app)
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@agent_routes.post('/api/agents/heartbeat')
async def heartbeat_handler(request):
    """Обновить heartbeat агента"""
    try:
        data = request._json_data if hasattr(request, '_json_data') else await request.json()
        result = await update_heartbeat(data, request.app)
        return web.json_response(result)
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@agent_routes.post('/api/agents')
async def create_agent_handler(request):
    """Создать нового агента"""
    try:
        data = request._json_data if hasattr(request, '_json_data') else await request.json()
        result = await create_agent(data, request.app)
        return web.json_response(result, status=201)
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@agent_routes.options('/api/agent/tasks')
async def options_agent_tasks_handler(request):
    """Обработка preflight запросов для CORS"""
    return web.Response()

@agent_routes.get('/api/agent/tasks')
async def get_agent_tasks_handler(request):
    """Получить задачи для агента"""
    try:
        result = await get_agent_tasks(request.app)
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@agent_routes.options('/api/agent/results')
async def options_agent_results_handler(request):
    """Обработка preflight запросов для CORS"""
    return web.Response()

@agent_routes.post('/api/agent/results')
async def send_agent_results_handler(request):
    """Отправить результаты выполнения задачи"""
    try:
        data = request._json_data if hasattr(request, '_json_data') else await request.json()
        result = await send_agent_results(data, request.app)
        return web.json_response(result)
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)