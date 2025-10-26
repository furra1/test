# Инструкция по деплою SPH

## Быстрый запуск (локально)

### 1. Клонировать репозиторий
```bash
git clone -b feature/2025-01-26-updates https://github.com/furra1/test.git
cd test
```

### 2. Запустить с Docker
```bash
docker-compose up -d --build
```

### 3. Проверить работу
```bash
# Проверить статус контейнеров
docker-compose ps

# Посмотреть логи
docker-compose logs -f

# Открыть в браузере
# http://localhost - главная страница
# http://localhost/html/history.html - история
# http://localhost/html/agents.html - агенты
```

## Деплой на Linux сервер

### Шаг 1: Подключись к серверу
```bash
ssh user@your-server.com
```

### Шаг 2: Установи Docker и Docker Compose
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 3: Склонируй проект
```bash
cd /opt
sudo git clone -b feature/2025-01-26-updates https://github.com/furra1/test.git sph
cd sph
```

### Шаг 4: Настрой домен в nginx конфиге
```bash
sudo nano docker/nginx.conf
# Измени server_name localhost на твой домен
```

### Шаг 5: Запусти Docker контейнеры
```bash
docker-compose up -d --build
```

### Шаг 6: Настрой Nginx на хосте (опционально, если нужен SSL)
```bash
# Если хочешь использовать домен с SSL через Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Управление

### Остановить
```bash
docker-compose down
```

### Перезапустить
```bash
docker-compose restart
```

### Обновить код
```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Посмотреть логи
```bash
# Все логи
docker-compose logs -f

# Логи backend
docker-compose logs -f backend

# Логи agent
docker-compose logs -f agent

# Логи nginx
docker-compose logs -f nginx
```

## Troubleshooting

### Порт занят
```bash
# Проверь какой процесс использует порт
sudo lsof -i :80
sudo lsof -i :8000

# Останови процесс или измени порт в docker-compose.yml
```

### Контейнеры не запускаются
```bash
# Проверь логи
docker-compose logs

# Удали старые контейнеры и пересобери
docker-compose down -v
docker-compose up -d --build
```

### БД не работает
```bash
# Проверь права на файл
ls -la agents.db

# Если нужно, удали старую БД и пересоздай
rm restApi/agents.db
docker-compose restart backend
```

## Переменные окружения

Создай файл `.env` для настройки:
```bash
# .env
PORT=8080
SERVER_URL=http://backend:8080
PYTHONPATH=/app/restApi
```

## Структура Docker

```
.
├── docker-compose.yml   # Основной файл оркестрации
├── Dockerfile            # Образ для backend и agent
├── requirements.txt     # Python зависимости
├── .dockerignore        # Что исключить из build
├── docker/
│   ├── nginx.conf      # Конфиг Nginx
│   └── README.md       # Дополнительная документация
└── DEPLOY.md          # Эта инструкция
```

## Команда для клонирования

```bash
git clone -b feature/2025-01-26-updates https://github.com/furra1/test.git
```

