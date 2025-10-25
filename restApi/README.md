# REST API для сетевых проверок

Система для выполнения различных сетевых проверок: ping, HTTP/HTTPS, TCP, DNS, traceroute.

## Установка

```bash
cd hakaton_preKolisty/restApi
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

Сервер запускается на `http://localhost:8000`

## API Эндпоинты

### 1. Создать проверку
**POST** `/api/check`

```json
{
  "target": "google.com",
  "checks": ["ping", "http", "dns"]
}
```

**Ответ:**
```json
{
  "checkId": "uuid-here",
  "status": "queued",
  "target": "google.com",
  "checks": ["ping", "http", "dns"]
}
```

### 2. Получить результат проверки
**GET** `/api/check/{check_id}`

**Ответ:**
```json
{
  "id": "uuid-here",
  "target": "google.com",
  "checks": ["ping", "http", "dns"],
  "status": "completed",
  "results": {
    "ping": {
      "success": true,
      "output": "..."
    },
    "http": {
      "success": true,
      "output": "..."
    },
    "dns": {
      "success": true,
      "output": "..."
    }
  }
}
```

## Типы проверок

| Тип | Описание | Пример |
|-----|----------|--------|
| `ping` | Проверка доступности ICMP | ping google.com |
| `http` | HTTP доступность | http://example.com |
| `https` | HTTPS доступность | https://example.com |
| `tcp` | TCP подключение | tcp к порту |
| `dns` | DNS записи | A, AAAA, MX, NS, TXT |
| `traceroute` | Маршрут пакетов | traceroute example.com |

## Примеры

### cURL

```bash
# Создать проверку
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "target": "google.com",
    "checks": ["ping", "dns"]
  }'

# Получить результат
curl http://localhost:8000/api/check/{check_id}
```

### JavaScript

```javascript
// Создать проверку
const response = await fetch('http://localhost:8000/api/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    target: 'google.com',
    checks: ['ping', 'http']
  })
});

const { checkId } = await response.json();

// Получить результат
const result = await fetch(`http://localhost:8000/api/check/${checkId}`);
const data = await result.json();
console.log(data);
```

## Структура проекта

```
restApi/
├── main.py              # Точка входа
├── app/
│   ├── server.py        # Настройка сервера, middleware
│   ├── routes/          # API эндпоинты
│   ├── handlers/        # Обработчики запросов
│   └── services/        # Бизнес-логика
├── PING.py              # Функция ping
├── HTTP.py              # Функция HTTP
├── TCP_connect.py       # TCP проверка
├── DNS.py               # DNS lookup
├── traceroute.py        # Traceroute
└── requirements.txt     # Зависимости
```

## Безопасность

- ✅ CORS с белым списком
- ✅ Rate limiting (100 req/min)
- ✅ Валидация JSON
- ✅ Защитные заголовки
- ✅ Логирование

Подробнее в [SECURITY.md](SECURITY.md)

## Troubleshooting

### Ошибка импорта модулей
Убедитесь что все файлы (PING.py, HTTP.py и т.д.) находятся в корне папки `restApi/`

### DNS не работает
Установите `dnspython`: `pip install dnspython`

### Traceroute не работает
На Windows используйте `tracert`, на Linux/Mac - `traceroute`
