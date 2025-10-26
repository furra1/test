# Деплой SPH с помощью Docker

## Быстрый старт

### 1. Собрать и запустить

```bash
docker-compose up -d --build
```

### 2. Проверить статус

```bash
docker-compose ps
```

### 3. Посмотреть логи

```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только agent
docker-compose logs -f agent
```

### 4. Остановить

```bash
docker-compose down
```

## Доступ к приложению

После запуска приложение будет доступно:
- Frontend: http://localhost
- API: http://localhost/api

## Проблемы?

### Проверить логи
```bash
docker-compose logs backend
docker-compose logs agent
docker-compose logs nginx
```

### Пересобрать
```bash
docker-compose down
docker-compose up -d --build --force-recreate
```

## Для production

1. Измени `docker/nginx.conf` - укажи свой домен
2. Настрой SSL сертификаты
3. Добавь `.env` файл с переменными окружения
4. Используй `docker-compose.prod.yml` для production настроек

