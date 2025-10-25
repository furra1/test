import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import uuid

# Добавляем путь к папке checks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'checks'))

# Импортируем функции проверок
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
        check_id = str(uuid.uuid4())
        
        self.checks_storage[check_id] = {
            "id": check_id,
            "target": target,
            "checks": checks,
            "status": "queued",
            "results": {},
            "created_at": None
        }
        
        asyncio.create_task(self._execute_checks(check_id, target, checks))
        return check_id
    
    async def _execute_checks(self, check_id: str, target: str, checks: List[str]):
        """Выполняет все проверки"""
        self.checks_storage[check_id]["status"] = "in_progress"
        results = {}
        
        for check_type in checks:
            try:
                if check_type == "ping":
                    results["ping"] = await self.run_ping_check(target)
                elif check_type == "http":
                    results["http"] = await self.run_http_check(target, is_https=False)
                elif check_type == "https":
                    results["https"] = await self.run_http_check(target, is_https=True)
                elif check_type == "tcp":
                    results["tcp"] = await self.run_tcp_check(target)
                elif check_type == "dns":
                    results["dns"] = await self.run_dns_check(target)
                elif check_type == "traceroute":
                    results["traceroute"] = await self.run_traceroute_check(target)
            except Exception as e:
                results[check_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        self.checks_storage[check_id]["results"] = results
        self.checks_storage[check_id]["status"] = "completed"
    
    def get_check_by_id(self, check_id: str) -> Dict[str, Any]:
        """Получает результат проверки по ID"""
        return self.checks_storage.get(check_id)
    
    def get_all_checks(self) -> List[Dict[str, Any]]:
        """Получает все проверки"""
        return list(self.checks_storage.values())