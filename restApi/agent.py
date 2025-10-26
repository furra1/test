#!/usr/bin/env python3
"""
Агент для выполнения сетевых проверок
Регистрируется в базе данных и выполняет задачи от сервера
"""

import asyncio
import aiohttp
import json
import time
import uuid
import socket
import platform
import subprocess
import sys
import os
from typing import Dict, List, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetworkAgent:
    """Агент для выполнения сетевых проверок"""
    
    def __init__(self, server_url: str = "http://localhost:8000", agent_name: str = None):
        self.server_url = server_url
        self.agent_name = agent_name or f"agent-{platform.node()}"
        self.agent_token = str(uuid.uuid4())
        self.location = self._get_location()
        self.ip = self._get_local_ip()
        self.agent_id = None
        self.running = False
        
        # Добавляем путь к модулям проверок
        checks_path = os.path.join(os.path.dirname(__file__), 'app', 'checks')
        sys.path.insert(0, checks_path)
        
        # Импортируем функции проверок
        try:
            # Сначала пробуем импортировать из ip_checks.py
            from ip_checks import (
                advanced_ping_check,
                http_ping_check,
                simple_tcp_ping,
                check_all_records,
                execute_traceroute
            )
            
            self.check_functions = {
                'ping': advanced_ping_check,
                'http': http_ping_check,
                'https': http_ping_check,
                'tcp': simple_tcp_ping,
                'dns': check_all_records,
                'traceroute': execute_traceroute
            }
        except ImportError:
            # Fallback к старым модулям если ip_checks.py не найден
            try:
                from PING import advanced_ping_check
                from HTTP import http_ping_check
                from TCP_connect import simple_tcp_ping
                from DNS import check_all_records
                from traceroute import execute_traceroute
                
                self.check_functions = {
                    'ping': advanced_ping_check,
                    'http': http_ping_check,
                    'https': http_ping_check,
                    'tcp': simple_tcp_ping,
                    'dns': check_all_records,
                    'traceroute': execute_traceroute
                }
            except ImportError as e:
                logger.error(f"Ошибка импорта модулей проверок: {e}")
                self.check_functions = {}
    
    def _get_location(self) -> str:
        """Получить локацию агента"""
        try:
            # Пробуем получить внешний IP
            import requests
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        except:
            pass
        return f"{platform.system()} {platform.release()}"
    
    def _get_local_ip(self) -> str:
        """Получить локальный IP адрес"""
        try:
            # Подключаемся к внешнему адресу для определения локального IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def register(self) -> bool:
        """Регистрация агента в базе данных"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'name': self.agent_name,
                    'location': self.location,
                    'ip': self.ip,
                    'token': self.agent_token
                }
                
                async with session.post(f"{self.server_url}/api/agents", json=data) as response:
                    if response.status == 201:
                        result = await response.json()
                        self.agent_id = result.get('agent_id')
                        logger.info(f"Агент зарегистрирован с ID: {self.agent_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка регистрации: {error}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при регистрации: {e}")
            return False
    
    async def send_heartbeat(self) -> bool:
        """Отправка heartbeat серверу"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'agent_id': self.agent_id,
                    'token': self.agent_token
                }
                
                async with session.post(f"{self.server_url}/api/agents/heartbeat", json=data) as response:
                    if response.status == 200:
                        logger.debug("Heartbeat отправлен успешно")
                        return True
                    else:
                        logger.warning(f"Heartbeat не отправлен: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при отправке heartbeat: {e}")
            return False
    
    def _capture_output(self, func, *args, **kwargs):
        """Выполняет функцию и перехватывает stdout"""
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            func(*args, **kwargs)
            output = captured_output.getvalue()
            return {"success": True, "output": output}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            sys.stdout = old_stdout
    
    async def execute_check(self, check_type: str, target: str) -> Dict[str, Any]:
        """Выполнение проверки"""
        logger.info(f"Выполняю проверку {check_type} для {target}")
        
        if check_type not in self.check_functions:
            return {
                "success": False,
                "error": f"Тип проверки {check_type} не поддерживается"
            }
        
        try:
            # Выполняем проверку в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._capture_output,
                self.check_functions[check_type],
                target,
                5 if check_type in ['ping', 'http', 'https', 'tcp'] else None
            )
            
            return {
                "type": check_type,
                "target": target,
                **result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Получение задач от сервера"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/agent/tasks") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('tasks', [])
                    else:
                        logger.warning(f"Не удалось получить задачи: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Ошибка при получении задач: {e}")
            return []
    
    async def send_results(self, task_id: str, results: Dict[str, Any]) -> bool:
        """Отправка результатов выполнения задачи"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'task_id': task_id,
                    'agent_id': self.agent_id,
                    'results': results
                }
                
                async with session.post(f"{self.server_url}/api/agent/results", json=data) as response:
                    if response.status == 200:
                        logger.info(f"Результаты для задачи {task_id} отправлены")
                        return True
                    else:
                        logger.error(f"Ошибка отправки результатов: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при отправке результатов: {e}")
            return False
    
    async def process_tasks(self):
        """Обработка задач"""
        while self.running:
            try:
                # Получаем задачи
                tasks = await self.get_tasks()
                
                for task in tasks:
                    task_id = task.get('id')
                    check_type = task.get('type')
                    target = task.get('target')
                    
                    if not all([task_id, check_type, target]):
                        continue
                    
                    logger.info(f"Обрабатываю задачу {task_id}: {check_type} {target}")
                    
                    # Выполняем проверку
                    result = await self.execute_check(check_type, target)
                    
                    # Отправляем результаты
                    await self.send_results(task_id, result)
                
                # Пауза между проверками задач
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке задач: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """Запуск агента"""
        logger.info(f"Запуск агента {self.agent_name}")
        logger.info(f"Локация: {self.location}")
        logger.info(f"IP: {self.ip}")
        logger.info(f"Токен: {self.agent_token}")
        
        # Регистрируемся
        if not await self.register():
            logger.error("Не удалось зарегистрироваться. Завершение работы.")
            return
        
        self.running = True
        
        # Запускаем обработку задач
        task_processor = asyncio.create_task(self.process_tasks())
        
        # Отправляем heartbeat каждые 30 секунд
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        try:
            # Ждем завершения задач
            await asyncio.gather(task_processor, heartbeat_task)
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
        finally:
            self.running = False
            task_processor.cancel()
            heartbeat_task.cancel()
            logger.info("Агент остановлен")
    
    async def _heartbeat_loop(self):
        """Цикл отправки heartbeat"""
        while self.running:
            await self.send_heartbeat()
            await asyncio.sleep(30)  # Heartbeat каждые 30 секунд

async def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Network Agent')
    parser.add_argument('--server', default='http://localhost:8000', help='URL сервера')
    parser.add_argument('--name', help='Имя агента')
    
    args = parser.parse_args()
    
    agent = NetworkAgent(server_url=args.server, agent_name=args.name)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
