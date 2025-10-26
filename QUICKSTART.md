# Быстрый старт SPH

## Локальный запуск (без Docker)

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Запустить сервисы (3 терминала)

**Терминал 1 - Backend:**
```bash
cd restApi
python main.py
```

**Терминал 2 - Agent:**
```bash
cd restApi
python run_agent.py
```

**Терминал 3 - Frontend:**
```bash
python -m http.server 8080
```

### 3. Откройте в браузере
- Главная: http://localhost:8080/html/index.html
- История: http://localhost:8080/html/history.html
- Агенты: http://localhost:8080/html/agents.html

---

## Docker запуск 

### 1. Клонировать
```bash
git clone -b feature/2025-01-26-updates https://github.com/furra1/test.git
cd test
```

### 2. Запустить
```bash
docker-compose up -d --build
```

### 3. Открыть
- Frontend: http://localhost
- API: http://localhost/api

### 4. Логи
```bash
docker-compose logs -f
```

### 5. Остановить
```bash
docker-compose down
```

---

## Деплой на Linux сервер

```bash
# 1. Подключись к серверу
ssh user@your-server.com

# 2. Установи Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Склонируй проект
cd /opt
sudo git clone -b feature/2025-01-26-updates https://github.com/furra1/test.git sph
cd sph

# 4. Настройка домена (опционально)
nano docker/nginx.conf
# Изменение server_name localhost на нужный домен

# 5. Запустить
docker-compose up -d --build

# 6. Проверить
docker-compose ps
```

---

## Проблемы?

### Локально не запускается
```bash
# Остановить все Python процессы
taskkill /f /im python.exe

# Перезапустить
```

### Docker не запускается
```bash
# Пересоберать
docker-compose down -v
docker-compose up -d --build --force-recreate
```

### Порт занят
```bash
# Изменить порт в docker-compose.yml
nano docker-compose.yml
# Измени 8000:8000 на 8080:8000
```

---

## Структура проекта

```
.
├── restApi/          # Backend Python приложение
│   ├── main.py      # Точка входа
│   ├── agent.py     # Агент для проверок
│   └── app/         # Основное приложение
├── html/            # Frontend HTML страницы
│   ├── index.html
│   ├── history.html
│   └── agents.html
├── js/              # JavaScript модули
├── docker-compose.yml  # Docker оркестрация
├── Dockerfile       # Docker образ
└── requirements.txt # Python зависимости
```

