# 🚀 Маршрутизация для Marzneshin

Один `subscription.py` для **любых** подписок (JSON и Non-JSON). Тип роутинга выбирается через переменную окружения.

## Установка

**1.** Скопируйте `subscription.py` на сервер:

```bash
curl -fLo /var/lib/marzneshin/subscription.py \
  https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/ADDON_AUTOROUTING/Marzneshin/subscription.py
```

**2.** Прилинкуйте файл в `docker-compose.yml` панели (`/etc/opt/marzneshin/docker-compose.yml`):

```yaml
services:
  marzneshin:
    volumes:
      - /var/lib/marzneshin:/var/lib/marzneshin
      - /var/lib/marzneshin/subscription.py:/app/app/routes/subscription.py   # ← добавить
```

**3.** *(опционально)* Выберите профиль роутинга через env var:

```yaml
    environment:
      CUSTOM_ROUTING_SOURCE: "default"   # default | jsonsub | whitelist | custom
      # CUSTOM_ROUTING_CUSTOM: "happ://..."  # только при source=custom
```

| Значение | Что отдаётся клиенту |
|---|---|
| `default` | Полный профиль: RU/BY direct, YouTube/Telegram/GitHub/Discord через прокси, реклама блокируется **(по умолчанию)** |
| `jsonsub` | Минимальный профиль для JSON-подписок: только DNS + кастомные geoip/geosite |
| `whitelist` | Direct только для белых списков РФ; всё остальное через прокси |
| `custom` | Ваша ссылка из `CUSTOM_ROUTING_CUSTOM` |

**4.** Перезагрузите Marzneshin:

```bash
marzneshin restart
```
