#!/usr/bin/env python3
"""
Скрипт для запуска агента
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from agent import NetworkAgent

async def main():
    """Запуск агента"""
    print("Запуск Network Agent")
    print("=" * 50)
    
    # Создаем агента
    server_url = os.environ.get('SERVER_URL', 'http://localhost:8000')
    agent = NetworkAgent(
        server_url=server_url,
        agent_name="Test Agent"
    )
    
    # Запускаем агента
    await agent.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nАгент остановлен пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
