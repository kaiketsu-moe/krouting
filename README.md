# 🚀 KRouting — Своя система правил маршрутизации

[![Happ](https://img.shields.io/badge/Happ-blue.svg)](https://happ.su)
[![Incy](https://img.shields.io/badge/Incy-darkgreen.svg)](https://incy.cc)
[![Mihomo](https://img.shields.io/badge/Mihomo-grey.svg)](https://github.com/MetaCubeX/mihomo)
[![jsDelivr](https://data.jsdelivr.com/v1/package/gh/kaiketsu-moe/krouting/badge)](https://www.jsdelivr.com/package/gh/kaiketsu-moe/krouting)

Готовые конфигурации маршрутизации для **Happ**, **INCY**, **Mihomo (Clash Meta)**, **Xray / V2Ray**, **sing-box** с Deeplink и автогенерацией собственных правил из исходников.

> Полный аналог [roscomvpn-routing](https://github.com/hydraponique/roscomvpn-routing), но с полностью управляемыми и кастомизируемыми списками: всё собирается из текстовых файлов в репозитории через GitHub Actions.

---

## 📱 Установка для Happ

| Профиль | Deeplink (в один клик) | JSON конфиг | Описание |
|---|---|---|---|
| **DEFAULT** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/DEFAULT.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/DEFAULT.JSON) | Полный профиль: RU/BY direct, YouTube, Telegram, GitHub, Discord, AI через прокси, реклама и трекеры блокируются |
| **WHITELIST** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/WHITELIST.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/WHITELIST.JSON) | Direct только для госсервисов и банков РФ; весь остальной интернет через прокси |
| **JSONSUB** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/JSONSUB.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/HAPP/JSONSUB.JSON) | Минимальный профиль: DNS + ссылки на ваши geoip.dat и geosite.dat |

*Импорт в Happ:* скопируйте ссылку на `.DEEPLINK` (схема `happ://routing/onadd/...`) и откройте на устройстве, либо импортируйте через меню маршрутизации.

---

## 📱 Установка для INCY

| Профиль | Deeplink (в один клик) | JSON конфиг | Описание |
|---|---|---|---|
| **DEFAULT** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/DEFAULT.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/DEFAULT.JSON) | Полный профиль со схемой `incy://routing/onadd/...` |
| **WHITELIST** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/WHITELIST.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/WHITELIST.JSON) | Белый список РФ direct, остальное через прокси |
| **JSONSUB** | [🔗 DEEPLINK](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/JSONSUB.DEEPLINK) | [📊 JSON](https://raw.githubusercontent.com/kaiketsu-moe/krouting/main/INCY/JSONSUB.JSON) | Минимальный профиль для INCY |

---

## 💻 Установка для Mihomo (Clash Meta)

В каталоге `MIHOMO/` подготовлены готовые конфигурации:

| Файл | Описание |
|---|---|
| [`MIHOMO/default.yaml`](MIHOMO/default.yaml) | Полный рабочий конфиг с группами прокси (`🛡️ VPN`, `📺 Youtube`, `💬 Discord.exe`, `🎮 Игры`, `⚡️ Авто`), TUN-режимом, защитой от утечек DNS и правилами `.mrs` |
| [`MIHOMO/template_remnawave.yaml`](MIHOMO/template_remnawave.yaml) | Шаблон для вставки в панель Remnawave |

---

## 🗺 Маршрутизация по умолчанию (DEFAULT)

### 🔴 Блокировка (REJECT)
- **Телеметрия и слежка Windows**: сбор телеметрии Microsoft
- **BitTorrent DHT & публичные трекеры**: экономия трафика сервера и защита от абуз
- **Реклама**: рекламные сети Яндекса, VK, Google Ads

### 🟢 Напрямую (DIRECT)
- **Российские и белорусские диапазоны IP**: CIDR из баз RIR + ваши исключения
- **Сервисы РФ**: VK, Mail.ru, OK, Яндекс, Госуслуги, ФНС (nalog.gov.ru)
- **Банки РФ**: Сбер, Т-Банк, Альфа, ВТБ, Райффайзен, Газпромбанк и др.
- **Игры**: Steam, Epic Games, Riot Games, Faceit, Escape from Tarkov
- **Apple & Microsoft**: системные обновления, CDN, push-уведомления
- **Twitch (видео-потоки)**: экономия трафика сервера
- **Pinterest**: загрузка картинок напрямую

### 🔵 Через VPN (PROXY)
- **YouTube**: борьба с ТСПУ и замедлениями
- **Telegram & Discord**: мессенджеры и голосовые каналы
- **GitHub**: обход блокировок и деградации
- **Google Play & сервисы Android**: обновления и сервисы
- **ИИ-сервисы**: OpenAI, ChatGPT, Claude / Anthropic
- **Twitch Ads**: обход рекламы через прокси-правила
- **Весь остальной заблокированный или зарубежный интернет**

---

## 🇷🇺 DNS

| Зона | DNS-сервер | Протокол |
|---|---|---|
| Domestic (direct) | [Яндекс DNS](https://dns.yandex.ru/) `77.88.8.8` | DoH (`https://77.88.8.8/dns-query`) |
| Remote (proxy) | [Google Public DNS](https://developers.google.com/speed/public-dns/) `8.8.8.8` | DoH (`https://8.8.8.8/dns-query`) |

В конфигах также настроен статический резолв для проблемных адресов ФНС (`lkfl2.nalog.ru`, `lknpd.nalog.ru`).

---

## 🔌 Интеграция с панелями подписок (`ADDON_AUTOROUTING`)

В папке `ADDON_AUTOROUTING/` лежат готовые модули инъекции deeplink-роутинга:

- **[Marzban](ADDON_AUTOROUTING/Marzban/README.md)**: скрипт `subscription.py` для автоматической отдачи заголовка `Routing:` в подписках.
- **[Marzneshin](ADDON_AUTOROUTING/Marzneshin/README.md)**: скрипт `subscription.py` с поддержкой переключения профилей (`default`, `whitelist`, `jsonsub`, `custom`).
- **[Remnawave](ADDON_AUTOROUTING/Remnawave/README.md)**: интеграция автообновления и шаблон `MIHOMO/template_remnawave.yaml`.
- **[3x-ui](ADDON_AUTOROUTING/3x-ui/README.md)**: указание ссылок на собранные `geosite.dat` и `geoip.dat`.

---

## 🛠 Как менять правила и добавлять свои

### Домены (`data/`)

Каждый файл в папке `data/` формирует отдельную категорию `geosite:<имя-файла>`:

- `data/my-proxy` — ваши сайты через VPN (поддерживает `include:`)
- `data/my-direct` — ваши сайты напрямую мимо VPN
- `data/my-block` — ваши сайты для блокировки
- `data/tspu-blocked`, `data/youtube`, `data/discord`, `data/games` и т.д.

Синтаксис v2fly:
```
domain:example.com        # домен и все его поддомены
full:sub.example.com      # только точное совпадение
keyword:example           # подстрока
include:youtube           # вставить содержимое другого файла
```

### IP-адреса (`ip/` и `geoip.config.json`)

- `ip/my-direct.txt` — ваши CIDR-диапазоны напрямую
- `ip/my-proxy.txt` — ваши CIDR-диапазоны через VPN
- `ip/exclude-from-direct.txt` — что исключить из российских CIDR (например, активы Cloudflare)
- `geoip.config.json` — конфигурация сборщика Loyalsoldier/geoip (подтягивает RIR RU/BY/KZ, Telegram CIDR и др.)

### Профили и настройки (`profiles.json`)

В `profiles.json` задаются:
- Ссылки на публикацию (`base_url`, `ruleset_base_url`, `raw_base_url`)
- Составы профилей `DEFAULT`, `WHITELIST`, `JSONSUB`
- DNS-серверы и статические хосты

---

## ⚙️ Сборка и CI/CD

### Локальная сборка

Для сборки требуются `go >= 1.22`, `python3`, `curl`, `bash`:

```bash
# Сборка только конфигураций HAPP, INCY, MIHOMO
python3 scripts/render_configs.py

# Полная сборка geosite.dat, geoip.dat, .srs, .mrs (скачивает тулзы в .tools/)
make build
```

### Автоматическая сборка в GitHub Actions (`.github/workflows/build.yml`)

1. При пуше изменений в `data/`, `ip/`, `profiles.json` или по расписанию (каждый четверг) запускается Action.
2. Компилируются `geosite.dat`, `geoip.dat`, sing-box `.srs` и mihomo `.mrs`.
3. Генерируются конфигурации и deeplink в `HAPP/`, `INCY/`, `MIHOMO/` и коммитятся в ветку `main`.
4. Создаётся GitHub Release с тегом таймстемпа.
5. Файлы публикуются в orphan-ветку `release` для доступа через **jsDelivr CDN**:
   `https://cdn.jsdelivr.net/gh/<owner>/<repo>@release/mihomo/geosite-youtube.mrs`
