# 🚀 Маршрутизация для Marzban

Один `subscription.py` для **любых** подписок (JSON и Non-JSON). Тип роутинга выбирается через переменную окружения.

## Установка

**1.** Скопируйте `subscription.py` на сервер:

```bash
curl -fLo /var/lib/marzban/subscription.py \
  https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/ADDON_AUTOROUTING/Marzban/subscription.py
```

**2.** Подключите volume в `docker-compose.yml` панели Marzban (`/opt/marzban/docker-compose.yml`):

```yaml
services:
  marzban:
    volumes:
      - /var/lib/marzban:/var/lib/marzban
      - /var/lib/marzban/subscription.py:/code/app/routes/subscription.py   # ← добавить
```

**3.** *(опционально)* Задайте профиль через переменную окружения:

```yaml
    environment:
      CUSTOM_ROUTING_SOURCE: "default"   # default | jsonsub | whitelist | custom
      # CUSTOM_ROUTING_CUSTOM: "happ://..."  # только при source=custom
```

| Значение | Что отдаётся клиенту |
|---|---|
| `default` | Полный профиль: RU/BY direct, YouTube/Telegram/GitHub/Discord через прокси, блокировка рекламы **(по умолчанию)** |
| `whitelist` | Direct только для белых списков РФ; всё остальное через прокси |
| `jsonsub` | Минимальный профиль для JSON-подписок: только DNS + кастомные geoip/geosite |
| `custom` | Ваша ссылка из `CUSTOM_ROUTING_CUSTOM` |

**4.** Перезагрузите Marzban:

```bash
marzban restart
```

Клиенты Happ и INCY при обновлении подписки автоматически получат роутинг в заголовке `Routing:`.
