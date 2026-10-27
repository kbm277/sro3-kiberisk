# СРО 3. Киберриск

Три контейнера:

| Что | Образ | Адрес |
| --- | --- | --- |
| Сайт | `cyberrisk-site:1.0` (свой Dockerfile на базе nginx) | http://localhost:8090 |
| Другой сервис | `redis:7-alpine` (официальный образ) | порт `6380`, проверка командой `ping` |
| Свой сервис | `cyberrisk-custom:1.0` (свой Python-код) | http://localhost:8081 |

## Запуск

Нужен запущенный Docker Desktop.

```bash
cd sro3-kiberisk
docker compose up -d --build
docker ps
```

Проверка Redis:

```bash
docker exec -it sro3-kiberisk-cache-1 redis-cli ping
```

Ответ `PONG` значит, что контейнер живой.

Остановка:

```bash
docker compose down
```

## Docker Hub

Образы `nginx` и `redis` уже лежат на Hub, их заливать не нужно. Сохраняют те образы, которые собраны здесь: `cyberrisk-site` и `cyberrisk-custom`.

### Регистрация

1. Открой https://hub.docker.com/signup
2. Укажи почту, логин латиницей и пароль. Логин дальше называется `USERNAME`.
3. Подтверди почту по письму.
4. Войди на сайт.

### Вход из терминала

```bash
docker login
```

Логин — тот же `USERNAME`. Пароль при вводе не виден. Успех: `Login Succeeded`.

Если сайт просит токен вместо пароля: **Account settings → Personal access tokens → Generate**. Токен вставляется в поле пароля команды `docker login`.

### Отправка образов

Подставь свой логин вместо `USERNAME`.

```bash
docker tag cyberrisk-site:1.0 USERNAME/cyberrisk-site:1.0
docker tag cyberrisk-custom:1.0 USERNAME/cyberrisk-custom:1.0

docker push USERNAME/cyberrisk-site:1.0
docker push USERNAME/cyberrisk-custom:1.0
```

Готовые страницы:

- https://hub.docker.com/r/USERNAME/cyberrisk-site
- https://hub.docker.com/r/USERNAME/cyberrisk-custom

На каждой должен быть тег `1.0`.
