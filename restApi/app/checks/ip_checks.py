import dns.resolver
import requests
import socket
import subprocess
import platform
import time
import statistics
import sys
from urllib.parse import urlparse
from typing import List, Dict, Optional

def normalize_domain(domain):
    """Извлекает домен из URL если необходимо"""
    if domain.startswith(('http://', 'https://')):
        parsed = urlparse(domain)
        return parsed.hostname or domain
    return domain



def get_dns_servers():
    """Возвращает список DNS серверов для использования"""
    return [
        '8.8.8.8', 
        '1.1.1.1', 
        '208.67.222.222',  
    ]

def dns_lookup(domain, record_type='A', dns_server=None):
    """
    Выполняет DNS запрос указанного типа
    """
    domain = normalize_domain(domain)
    
    try:
        resolver = dns.resolver.Resolver()
        
        if dns_server:
            resolver.nameservers = [dns_server]
        
        answers = resolver.resolve(domain, record_type)
        
        results = []
        for rdata in answers:
            results.append(str(rdata))
        
        return {
            'success': True,
            'domain': domain,
            'type': record_type,
            'results': results,
            'dns_server': dns_server or 'system'
        }
        
    except dns.resolver.NoAnswer:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': f'No {record_type} record found',
            'dns_server': dns_server or 'system'
        }
    except dns.resolver.NXDOMAIN:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': 'Domain does not exist',
            'dns_server': dns_server or 'system'
        }
    except dns.resolver.Timeout:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': 'DNS query timed out',
            'dns_server': dns_server or 'system'
        }
    except Exception as e:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': f'Error: {str(e)}',
            'dns_server': dns_server or 'system'
        }

def check_all_records(domain, dns_server=None):
    """
    Проверяет все основные типы DNS записей для домена
    """
    domain = normalize_domain(domain)
    
    print(f"\nDNS LOOKUP {domain}")
    if dns_server:
        print(f"DNS Server: {dns_server}")
    print("─" * 60)
    
    record_types = [
        ('A', 'IPv4 addresses'),
        ('AAAA', 'IPv6 addresses'),
        ('MX', 'Mail servers'),
        ('NS', 'Name servers'),
        ('TXT', 'Text records'),
        ('CNAME', 'Canonical name'),
        ('SOA', 'Start of authority')
    ]
    
    all_results = {}
    
    for record_type, description in record_types:
        print(f"\n{record_type:6} ({description}):")
        print("  " + "─" * 50)
        
        result = dns_lookup(domain, record_type, dns_server)
        all_results[record_type] = result
        
        if result['success']:
            for i, record in enumerate(result['results'], 1):
                if record_type == 'MX':
                    parts = record.split()
                    if len(parts) >= 2:
                        priority = parts[0]
                        server = ' '.join(parts[1:])
                        print(f"  {i:2d}. Priority: {priority}, Server: {server}")
                    else:
                        print(f"  {i:2d}. {record}")
                else:
                    print(f"{i:2d}. {record}")
        else:
            print(f"{result['error']}")
    
    return all_results

def check_with_multiple_dns(domain):
    """
    Проверяет DNS записи используя несколько DNS серверов
    """
    domain = normalize_domain(domain)
    dns_servers = get_dns_servers()
    
    print(f"\nDNS LOOKUP {domain} - Multiple DNS Servers")
    print("─" * 60)
    
    for dns_server in dns_servers:
        print(f"\n📡 Using DNS: {dns_server}")
        result = dns_lookup(domain, 'A', dns_server)
        
        if result['success']:
            print(f" A records: {', '.join(result['results'])}")
        else:
            print(f"{result['error']}")

def detailed_mx_check(domain):
    """
    Детальная проверка MX записей с проверкой A записей для mail серверов
    """
    domain = normalize_domain(domain)
    
    print(f"\nDETAILED MX CHECK {domain}")
    print("─" * 60)
    
    mx_result = dns_lookup(domain, 'MX')
    
    if not mx_result['success']:
        print(f"{mx_result['error']}")
        return
    
    print("MX Records found:")
    for i, mx_record in enumerate(mx_result['results'], 1):
        parts = mx_record.split()
        if len(parts) >= 2:
            priority = parts[0]
            mail_server = ' '.join(parts[1:])
            
            print(f"\n{i}. Mail Server: {mail_server}")
            print(f"   Priority: {priority}")
            
            a_result = dns_lookup(mail_server, 'A')
            if a_result['success']:
                print(f"   IPv4: {', '.join(a_result['results'])}")
            else:
                print(f"   IPv4: Not found")
            
            aaaa_result = dns_lookup(mail_server, 'AAAA')
            if aaaa_result['success']:
                print(f"   IPv6: {', '.join(aaaa_result['results'])}")

def dns_benchmark(domain):
    """
    Тестирование скорости ответа разных DNS серверов
    """
    domain = normalize_domain(domain)
    dns_servers = get_dns_servers()
    
    print(f"\nDNS BENCHMARK {domain}")
    print("─" * 60)
    
    results = []
    
    for dns_server in dns_servers:
        start_time = time.time()
        result = dns_lookup(domain, 'A', dns_server)
        response_time = (time.time() - start_time) * 1000  
        
        status = 'Выполнено' if result['success'] else 'Отказ'
        results.append({
            'server': dns_server,
            'time': response_time,
            'success': result['success'],
            'records': result['results'] if result['success'] else []
        })
        
        if result['success']:
            print(f"{status} {dns_server:15} - {response_time:6.1f} ms - {', '.join(result['results'])}")
        else:
            print(f"{status} {dns_server:15} - {response_time:6.1f} ms - {result['error']}")
    
    successful_results = [r for r in results if r['success']]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x['time'])
        print(f"\n🏆 Fastest DNS: {fastest['server']} ({fastest['time']:.1f} ms)")

def quick_dns_check(domain):
    """Быстрая проверка основных DNS записей"""
    return check_all_records(domain)

def get_domain_ips(domain):
    """Возвращает все IP адреса домена"""
    domain = normalize_domain(domain)
    results = {}
    
    a_result = dns_lookup(domain, 'A')
    if a_result['success']:
        results['ipv4'] = a_result['results']
    
    aaaa_result = dns_lookup(domain, 'AAAA')
    if aaaa_result['success']:
        results['ipv6'] = aaaa_result['results']
    
    return results

def check_dns_health(domain):
    """Проверяет здоровье DNS конфигурации домена"""
    domain = normalize_domain(domain)
    
    print(f"\nDNS HEALTH CHECK {domain}")
    print("─" * 60)
    
    checks = [
        ('A', 'IPv4 addresses', True),
        ('NS', 'Name servers', True),
        ('MX', 'Mail servers', False),  
        ('SOA', 'Start of authority', True)
    ]
    
    health_status = True
    
    for record_type, description, required in checks:
        result = dns_lookup(domain, record_type)
        
        if result['success']:
            print(f" {record_type}: {len(result['results'])} records found")
        else:
            if required:
                print(f" {record_type}: {result['error']}")
                health_status = False
            else:
                print(f"  {record_type}: {result['error']} (optional)")
    
    if health_status:
        print(f"\n DNS configuration looks healthy")
    else:
        print(f"\n  DNS configuration has issues")



def http_ping_check(url, count=5):
    """
    Выполняет многократную проверку доступности сайта по HTTP/HTTPS
    с выводом статистики в формате, похожем на ping
    """
 
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme
    port = parsed_url.port or (443 if scheme == 'https' else 80)

    print(f"HTTP PING {hostname} ({scheme.upper()}:{port})")

    success_count = 0
    response_times = []
    status_codes = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=True)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  
            response_times.append(response_time)
            status_codes.append(response.status_code)
            success_count += 1

           
            print(
                f"HTTP seq={i + 1} status={response.status_code} time={response_time:.1f} ms size={len(response.content)} bytes")

        except requests.exceptions.RequestException as e:
            print(f"HTTP seq={i + 1} failed: {str(e)}")
            response_times.append(None)
            status_codes.append(None)

    
        if i < count - 1:
            time.sleep(1)

    
    print(f"\n--- {hostname} HTTP ping statistics ---")
    packet_loss = ((count - success_count) / count) * 100
    print(f"{count} requests made, {success_count} successful, {packet_loss:.0f}% failed")

   
    successful_codes = [code for code in status_codes if code is not None]
    if successful_codes:
        code_counts = {}
        for code in successful_codes:
            code_counts[code] = code_counts.get(code, 0) + 1

        print("Status code distribution:")
        for code, count_val in code_counts.items():
            print(f"  {code}: {count_val} times")

    successful_times = [t for t in response_times if t is not None]
    if successful_times:
        min_time = min(successful_times)
        avg_time = statistics.mean(successful_times)
        max_time = max(successful_times)

        deviations = [abs(t - avg_time) for t in successful_times]
        mdev = statistics.mean(deviations) if deviations else 0

        print(f"response min/avg/max/mdev = {min_time:.3f}/{avg_time:.3f}/{max_time:.3f}/{mdev:.3f} ms")


def advanced_ping_check(url, count=5):
    """
    Выполняет многократную проверку пинга и выводит статистику в формате ping
    """
  
    if url.startswith(('http://', 'https://')):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
    else:
        hostname = url

 
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"ping: cannot resolve {hostname}: Unknown host")
        return

    print(f"PING {hostname} ({ip_address}) 56(84) bytes of data.")

    success_count = 0
    ping_times = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(f"https://{hostname}", timeout=10)
            end_time = time.time()

            ping_time = (end_time - start_time) * 1000  
            ping_times.append(ping_time)
            success_count += 1

        
            print(f"64 bytes from {hostname} ({ip_address}): icmp_seq={i + 1} ttl=54 time={ping_time:.1f} ms")

        except requests.exceptions.RequestException as e:
            print(f"From {ip_address} icmp_seq={i + 1} Destination Host Unreachable")
            ping_times.append(None)

        
        if i < count - 1:
            time.sleep(1)

  
    print(f"\n--- {hostname} ping statistics ---")
    packet_loss = ((count - success_count) / count) * 100
    print(
        f"{count} packets transmitted, {success_count} received, {packet_loss:.0f}% packet loss, time {count * 1000}ms")

    successful_pings = [t for t in ping_times if t is not None]
    if successful_pings:
        min_time = min(successful_pings)
        avg_time = statistics.mean(successful_pings)
        max_time = max(successful_pings)

        
        deviations = [abs(t - avg_time) for t in successful_pings]
        mdev = statistics.mean(deviations) if deviations else 0

        print(f"rtt min/avg/max/mdev = {min_time:.3f}/{avg_time:.3f}/{max_time:.3f}/{mdev:.3f} ms")



def simple_tcp_ping(url, count=5, port=None):
    """
    Упрощенная версия TCP ping с возможностью указания порта
    """
  
    if url.startswith(('http://', 'https://')):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not port:  
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    else:
        hostname = url
        if not port:
            port = 80  

    
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"Ошибка: не удается разрешить {hostname}")
        return

    print(f"TCP PING {hostname} ({ip_address}):{port}")

    times = []
    successful = 0

    for i in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            start = time.time()
            sock.connect((ip_address, port))
            elapsed = (time.time() - start) * 1000
            sock.close()

            times.append(elapsed)
            successful += 1
            print(f"tcp_seq={i + 1} connect time={elapsed:.1f} ms")

        except socket.timeout:
            print(f"tcp_seq={i + 1} timeout")
            times.append(None)
        except Exception as e:
            print(f"tcp_seq={i + 1} failed: {e}")
            times.append(None)

        if i < count - 1:
            time.sleep(1)

   
    print(f"\n--- {hostname}:{port} tcp statistics ---")
    loss = ((count - successful) / count) * 100
    print(f"{count} attempts, {successful} successful, {loss:.0f}% failure")

    good_times = [t for t in times if t is not None]
    if good_times:
        min_t = min(good_times)
        avg_t = statistics.mean(good_times)
        max_t = max(good_times)
        dev_t = statistics.mean([abs(t - avg_t) for t in good_times])
        print(f"connect min/avg/max/dev = {min_t:.3f}/{avg_t:.3f}/{max_t:.3f}/{dev_t:.3f} ms")



def get_traceroute_command(hostname, max_hops):
    """Возвращает команду traceroute для текущей ОС"""
    if platform.system().lower() == "windows":
        return ["tracert", "-h", str(max_hops), "-w", "3000", hostname]
    else:
        return ["traceroute", "-m", str(max_hops), "-w", "3", "-q", "1", hostname]

def fix_encoding(text):
    """Исправляет проблемы с кодировкой текста"""
    try:
        
        for encoding in ['utf-8', 'cp866', 'cp1251', 'iso-8859-1']:
            try:
                return text.encode('utf-8').decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
        return text
    except:
        return text

def execute_traceroute(hostname, max_hops=30):
    """
    Выполняет трассировку маршрута к указанному хосту
    """
   
    target = normalize_domain(hostname)
    
    print(f"\nTRACEROUTE {target}")
    print(f"Максимум прыжков: {max_hops}")
    print("─" * 60)
    
    try:
        
        command = get_traceroute_command(target, max_hops)
        
       
        if platform.system().lower() == "windows":
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='cp866',  
                timeout=120
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',  
                timeout=120
            )
        
      
        if result.returncode == 0:
            output = fix_encoding(result.stdout)
            print(output)
            return True
        else:
            error_msg = fix_encoding(result.stderr)
            if "не найден" in error_msg or "not found" in error_msg:
                print("Ошибка: Команда traceroute/tracert не найдена")
                print("Убедитесь, что traceroute установлен в системе")
            else:
                print(f"Ошибка выполнения: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Таймаут: трассировка заняла слишком много времени")
        return False
    except FileNotFoundError:
        print("Ошибка: Команда traceroute/tracert недоступна")
        print("\nДля установки:")
        if platform.system().lower() == "windows":
            print("• Traceroute встроен в Windows как 'tracert'")
        else:
            print("• Ubuntu/Debian: sudo apt install traceroute")
            print("• CentOS/RHEL: sudo yum install traceroute")
            print("• macOS: предустановлен")
        return False
    except UnicodeDecodeError as e:
        print(f"Ошибка кодировки: {e}")
        print("Попробуйте изменить настройки консоли")
        return False
    except Exception as error:
        print(f"Неожиданная ошибка: {error}")
        return False

def execute_traceroute_windows_fixed(hostname, max_hops=30):
    """Версия для Windows с исправлением кодировки через chcp"""
    if platform.system().lower() != "windows":
        return execute_traceroute(hostname, max_hops)
    
    target = normalize_domain(hostname)
    
    print(f"\nTRACEROUTE {target}")
    print(f"Максимум прыжков: {max_hops}")
    print("─" * 60)
    
    try:
       
        chcp_result = subprocess.run(["chcp", "65001"], capture_output=True, shell=True)
        
    
        command = ["tracert", "-h", str(max_hops), "-w", "3000", target]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Ошибка: {result.stderr}")
            return False
            
    except Exception as error:
        print(f"Ошибка: {error}")
        return False



def main():
    """Основная функция программы"""
    print("КОМПЛЕКСНАЯ ПРОВЕРКА СЕТИ")
    print("=" * 50)
    
    
    try:
        import dns.resolver
        import requests
    except ImportError as e:
        print(f"Ошибка: Не установлены необходимые библиотеки")
        print(f"Установите: pip install dnspython requests")
        sys.exit(1)
    
  
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("Введите домен или URL для проверки: ").strip()
        if not domain:
            print("Не указан домен")
            return
    
    domain = normalize_domain(domain)
    
    while True:
        print(f"\nЦелевой домен: {domain}")
        print("\nВыберите тип проверки:")
        print("1 - DNS: Полная проверка всех записей")
        print("2 - DNS: Проверка с разными DNS серверами")
        print("3 - DNS: Детальная проверка MX записей")
        print("4 - DNS: Бенчмарк DNS серверов")
        print("5 - DNS: Проверка конкретного типа записи")
        print("6 - DNS: Проверка здоровья конфигурации")
        print("7 - HTTP: Проверка доступности сайта")
        print("8 - PING: Проверка пинга")
        print("9 - TCP: Проверка TCP соединения")
        print("10 - TRACEROUTE: Трассировка маршрута")
        print("11 - ВСЕ ПРОВЕРКИ (комплексный анализ)")
        print("0 - Выход")
        print("c - Сменить домен")
        
        choice = input("\nВаш выбор [1]: ").strip().lower() or "1"
        
        if choice == "0":
            print("Выход из программы")
            break
        elif choice == "c":
            new_domain = input("Введите новый домен: ").strip()
            if new_domain:
                domain = normalize_domain(new_domain)
            continue
        
        try:
            if choice == "1":
                check_all_records(domain)
            elif choice == "2":
                check_with_multiple_dns(domain)
            elif choice == "3":
                detailed_mx_check(domain)
            elif choice == "4":
                dns_benchmark(domain)
            elif choice == "5":
                record_type = input("Введите тип записи (A, AAAA, MX, NS, TXT, CNAME): ").strip().upper()
                if record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']:
                    result = dns_lookup(domain, record_type)
                    print(f"\n{record_type} records for {domain}:")
                    if result['success']:
                        for i, record in enumerate(result['results'], 1):
                            print(f" {i}. {record}")
                    else:
                        print(f" {result['error']}")
                else:
                    print("Неверный тип DNS записи")
            elif choice == "6":
                check_dns_health(domain)
            elif choice == "7":
                http_ping_check(domain)
            elif choice == "8":
                advanced_ping_check(domain)
            elif choice == "9":
                port_input = input("Порт (по умолчанию автоопределение): ").strip()
                port = int(port_input) if port_input else None
                simple_tcp_ping(domain, 5, port)
            elif choice == "10":
                try:
                    hops_input = input("Максимум прыжков [30]: ").strip()
                    max_hops = int(hops_input) if hops_input else 30
                except ValueError:
                    max_hops = 30
                
                if platform.system().lower() == "windows":
                    execute_traceroute_windows_fixed(domain, max_hops)
                else:
                    execute_traceroute(domain, max_hops)
            elif choice == "11":
                print(f"\n{'='*60}")
                print(f"КОМПЛЕКСНЫЙ АНАЛИЗ ДОМЕНА: {domain}")
                print(f"{'='*60}")
                
         
                check_all_records(domain)
                dns_benchmark(domain)
                check_dns_health(domain)
                
              
                http_ping_check(domain)
                advanced_ping_check(domain)
                simple_tcp_ping(domain)
                
          
                if platform.system().lower() == "windows":
                    execute_traceroute_windows_fixed(domain)
                else:
                    execute_traceroute(domain)
                    
                print(f"\n{'='*60}")
                print("КОМПЛЕКСНЫЙ АНАЛИЗ ЗАВЕРШЕН")
                print(f"{'='*60}")
            else:
                print("Неверный выбор")
        
        except KeyboardInterrupt:
            print("\n\nПроверка прервана пользователем")
            continue
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            continue
        
       
        if choice != "11":  
            input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")