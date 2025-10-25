from aiohttp import web
from app.handlers.check_handler import create_check, get_check_result

checks_routes = web.RouteTableDef()

@checks_routes.options('/api/check')
async def options_check_handler(request):
    """Обработка preflight запросов для CORS"""
    return web.Response()

@checks_routes.post('/api/check')
async def create_check_handler(request):
    """Создать новую проверку"""
    try:
        data = request._json_data if hasattr(request, '_json_data') else await request.json()
        result = await create_check(data, request.app)
        return web.json_response(result, status=201)
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": f"Internal error: {str(e)}"}, status=500)

@checks_routes.options('/api/check/{check_id}')
async def options_get_check_handler(request):
    """Обработка preflight запросов для CORS"""
    return web.Response()

@checks_routes.get('/api/check/{check_id}')
async def get_check_handler(request):
    """Получить результат проверки"""
    check_id = request.match_info['check_id']
    result = await get_check_result(check_id, request.app)
    
    if result.get("status") == "not_found":
        return web.json_response(result, status=404)
    
    return web.json_response(result)