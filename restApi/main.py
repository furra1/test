from app.server import create_app
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    
    logger.info("Запуск REST API сервера...")
    logger.info("Сервер будет доступен на http://localhost:8000")
    
    import aiohttp.web
    port = int(os.environ.get('PORT', '8080'))
    aiohttp.web.run_app(
        app,
        host='0.0.0.0',
        port=port
    )