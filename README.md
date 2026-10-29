# СРО 3. Киберриск

Скачать проект одной командой:

```bash
git clone https://github.com/kbm277/sro3-kiberisk.git
cd sro3-kiberisk
docker compose up -d --build
```

После этого открой http://localhost:8090

Пять контейнеров одной командой Compose:

| Сервис | Образ на Docker Hub | Адрес |
| --- | --- | --- |
| Сайт | `kbm277/cyberrisk-site:1.0` | http://localhost:8090 |
| Свой реестр рисков | `kbm277/cyberrisk-custom:1.0` | http://localhost:8081 |
| Кэш Redis | `kbm277/cyberrisk-cache:1.0` | порт `6380` |
| База PostgreSQL | `kbm277/cyberrisk-db:1.0` | порт `5433`, база `risks`, пользователь `cyber`, пароль `cyberlab` |
| Мониторинг | `kbm277/cyberrisk-monitor:1.0` | http://localhost:8082 |

## Как работает Docker Compose

`docker-compose.yml` описывает весь стенд. Compose читает файл и делает четыре вещи:

1. **Собирает** свои образы из папок `site`, `custom`, `cache`, `db`, `monitor`.
2. **Создаёт одну сеть.** Сервисы видят друг друга по имени: `site`, `custom`, `cache`, `db`, `monitor`. Монитор именно так проверяет остальных.
3. **Публикует порты** в виде `порт_на_компьютере:порт_в_контейнере`. Снаружи сайт открыт на `8090`, внутри nginx слушает `80`.
4. **Ждёт готовности.** У каждого сервиса есть `healthcheck`. Монитор стартует, когда остальные четыре уже отвечают.

Полезные команды:

```bash
docker compose up -d --build   # собрать и запустить все пять
docker compose ps              # статус
docker compose push            # отправить все пять образов на Docker Hub
docker compose down            # остановить и убрать контейнеры
```

Проверка Redis и базы:

```bash
docker exec -it sro3-kiberisk-cache-1 redis-cli ping
docker exec -it sro3-kiberisk-db-1 psql -U cyber -d risks -c "SELECT asset, likelihood * impact AS score FROM risks;"
```

Ответ Redis — `PONG`. В базе пять строк реестра.

## Docker Hub

Образы подписаны логином `kbm277`, поэтому `docker compose push` кладёт их сразу в нужные репозитории:

- https://hub.docker.com/r/kbm277/cyberrisk-site
- https://hub.docker.com/r/kbm277/cyberrisk-custom
- https://hub.docker.com/r/kbm277/cyberrisk-cache
- https://hub.docker.com/r/kbm277/cyberrisk-db
- https://hub.docker.com/r/kbm277/cyberrisk-monitor

Перед отправкой нужен вход:

```bash
docker login
docker compose push
```

На каждой странице Hub должен быть тег `1.0`.

Чужой компьютер поднимает тот же стенд уже без сборки, если в `docker-compose.yml` оставить поле `image` и убрать `build`. Для этой работы `build` оставлен: так видно, из какого Dockerfile собран каждый образ.

## GitLab

Файл `.gitlab-ci.yml` повторяет локальные команды на сервере GitLab.

1. Создай пустой проект на GitLab и добавь его вторым remote:

```bash
git remote add gitlab https://gitlab.com/ЛОГИН/sro3-kiberisk.git
git push gitlab main
```

2. В проекте открой **Settings → CI/CD → Variables** и добавь `DOCKERHUB_USER` и `DOCKERHUB_TOKEN` (токен Docker Hub, флаг Masked).
3. Пайплайн на ветке `main` выполнит `docker compose build`, затем `docker compose push`.

Код работы лежит на GitHub: https://github.com/kbm277/sro3-kiberisk
