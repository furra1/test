from app.server import create_app
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    
    logger.info("Запуск REST API сервера...")
    logger.info("Сервер будет доступен на http://localhost:8000")
    
    import aiohttp.web
    aiohttp.web.run_app(
        app,
        host='0.0.0.0',
        port=8000
    )