#!/usr/bin/env bash
# Единый источник правды: какие geosite-списки публикуем как отдельные рулсеты.
# Правь этот список, когда добавляешь новый файл в data/.
export GEOSITE_LISTS="my-direct,my-proxy,my-block,ru-services,banks-ru,games,tspu-blocked,win-spy,ads,private,youtube,telegram,discord,github,google-play,openai,apple,microsoft,twitch,twitch-ads,pinterest,torrent,whitelist"

# Какие geoip-категории публикуем (совпадают с "name" в geoip.config.json).
export GEOIP_LISTS="direct,proxy,telegram,private,whitelist"
