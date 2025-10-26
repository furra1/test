import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import uuid

# Добавляем путь к папке checks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'checks'))

# Импортируем функции проверок из ip_checks.py
try:
    from ip_checks import (
        advanced_ping_check,
        http_ping_check,
        simple_tcp_ping,
        check_all_records,
        execute_traceroute
    )
except ImportError:
    # Fallback к старым модулям если ip_checks.py не найден
    try:
        from PING import advanced_ping_check
    except ImportError:
        def advanced_ping_check(target, count=5):
            return {"error": "Ping check not available"}
    
    try:
        from HTTP import http_ping_check
    except ImportError:
        def http_ping_check(target, count=5):
            return {"error": "HTTP check not available"}

    try:
        from TCP_connect import simple_tcp_ping
    except ImportError:
        def simple_tcp_ping(target, count=5, port=None):
            return {"error": "TCP check not available"}

    try:
        from DNS import check_all_records
    except ImportError:
        def check_all_records(target, dns_server=None):
            return {"error": "DNS check not available"}

    try:
        from traceroute import execute_traceroute
    except ImportError:
        def execute_traceroute(target, max_hops=30):
            return {"error": "Traceroute not available"}

class CheckService:
    """Сервис для выполнения различных сетевых проверок"""
    
    def __init__(self):
        self.checks_storage = {}  # Временное хранилище результатов
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _run_in_executor(self, func, *args, **kwargs):
        """Запускает синхронную функцию в отдельном потоке"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, func, *args, **kwargs)
    
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
    
    async def run_ping_check(self, target: str) -> Dict[str, Any]:
        """Выполняет ping проверку"""
        result = await self._run_in_executor(
            self._capture_output, 
            advanced_ping_check, 
            target, 
            5
        )
        return {
            "type": "ping",
            "target": target,
            **result
        }
    
    async def run_http_check(self, target: str, is_https: bool = False) -> Dict[str, Any]:
        """Выполняет HTTP/HTTPS проверку"""
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}" if is_https else f"http://{target}"
        
        result = await self._run_in_executor(
            self._capture_output,
            http_ping_check,
            target,
            5
        )
        return {
            "type": "https" if is_https else "http",
            "target": target,
            **result
        }
    
    async def run_tcp_check(self, target: str) -> Dict[str, Any]:
        """Выполняет TCP проверку"""
        result = await self._run_in_executor(
            self._capture_output,
            simple_tcp_ping,
            target,
            5,
            None
        )
        return {
            "type": "tcp",
            "target": target,
            **result
        }
    
    async def run_dns_check(self, target: str) -> Dict[str, Any]:
        """Выполняет DNS проверку"""
        result = await self._run_in_executor(
            self._capture_output,
            check_all_records,
            target,
            None
        )
        return {
            "type": "dns",
            "target": target,
            **result
        }
    
    async def run_traceroute_check(self, target: str) -> Dict[str, Any]:
        """Выполняет traceroute"""
        result = await self._run_in_executor(
            self._capture_output,
            execute_traceroute,
            target,
            30
        )
        return {
            "type": "traceroute",
            "target": target,
            **result
        }
    
    async def create_check(self, target: str, checks: List[str]) -> str:
        """Создает новую проверку и возвращает ID"""
        import datetime
        
        check_id = str(uuid.uuid4())
        
        self.checks_storage[check_id] = {
            "id": check_id,
            "target": target,
            "checks": checks,
            "status": "queued",
            "results": {},
            "created_at": datetime.datetime.now()
        }
        
        asyncio.create_task(self._execute_checks(check_id, target, checks))
        return check_id
    
    async def _execute_checks(self, check_id: str, target: str, checks: List[str]):
        """Выполняет все проверки"""
        self.checks_storage[check_id]["status"] = "in_progress"
        results = {}
        agent_results = []
        
        for check_type in checks:
            try:
                result = None
                if check_type == "ping":
                    result = await self.run_ping_check(target)
                elif check_type == "http":
                    result = await self.run_http_check(target, is_https=False)
                elif check_type == "https":
                    result = await self.run_http_check(target, is_https=True)
                elif check_type == "tcp":
                    result = await self.run_tcp_check(target)
                elif check_type == "dns":
                    result = await self.run_dns_check(target)
                elif check_type == "traceroute":
                    result = await self.run_traceroute_check(target)
                
                # Сохраняем в старом формате
                if result:
                    results[check_type] = result
                    
                    # Добавляем в новый формат для фронтенда
                    output = result.get('output', '')
                    success = result.get('success', False)
                    
                    agent_results.append({
                        "agent_id": "localhost",
                        "check_type": check_type,
                        "status": "completed" if success else "error",
                        "log": output,
                        "success": success
                    })
            except Exception as e:
                error_msg = str(e)
                results[check_type] = {
                    "success": False,
                    "error": error_msg
                }
                
                # Добавляем ошибку в новый формат
                agent_results.append({
                    "agent_id": "localhost",
                    "check_type": check_type,
                    "status": "error",
                    "log": f"Ошибка: {error_msg}",
                    "success": False
                })
        
        self.checks_storage[check_id]["results"] = results
        self.checks_storage[check_id]["agent_results"] = agent_results
        self.checks_storage[check_id]["status"] = "completed"
    
    def get_check_by_id(self, check_id: str) -> Dict[str, Any]:
        """Получает результат проверки по ID"""
        check_data = self.checks_storage.get(check_id)
        if not check_data:
            return None
        
        # Если есть новая структура (agent_results), используем её для фронтенда
        if 'agent_results' in check_data:
            return {
                "id": check_data.get('id'),
                "target": check_data.get('target'),
                "checks": check_data.get('checks', []),
                "status": check_data.get('status'),
                "results": check_data.get('agent_results', [])
            }
        
        # Иначе преобразуем старую структуру в новый формат
        legacy_results = check_data.get('results', {})
        agent_results = []
        
        for check_type, result in legacy_results.items():
            output = result.get('output', '') if isinstance(result, dict) else ''
            success = result.get('success', False) if isinstance(result, dict) else False
            
            agent_results.append({
                "agent_id": "localhost",
                "check_type": check_type,
                "status": "completed" if success else "error",
                "log": output,
                "success": success
            })
        
        return {
            "id": check_data.get('id'),
            "target": check_data.get('target'),
            "checks": check_data.get('checks', []),
            "status": check_data.get('status'),
            "results": agent_results
        }
    
    def get_all_checks(self) -> List[Dict[str, Any]]:
        """Получает все проверки"""
        return list(self.checks_storage.values())