#!/usr/bin/env python3
"""Рендер конфигов роутинга из profiles.json.

Генерирует файлы как в репозиторий (HAPP/, INCY/, MIHOMO/),
так и в каталог dist/ для релизов и артефактов:
  HAPP/<PROFILE>.JSON + .DEEPLINK       (схема happ://routing/onadd/<base64>)
  INCY/<PROFILE>.JSON + .DEEPLINK       (схема incy://routing/onadd/<base64>)
  MIHOMO/default.yaml                   (для ручной вставки в Mihomo/Clash Meta)
  MIHOMO/template_remnawave.yaml        (шаблон для панели Remnawave)
  xray/<PROFILE>.json                   (секция routing + dns для Xray/V2Ray)
"""
import base64
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "profiles.json").read_text(encoding="utf-8"))

PUB = CFG["publish"]
DNS = CFG["dns"]
DNS_HOSTS = CFG.get("dns_hosts", {})
STAMP = time.strftime("%Y%m%d%H%M", time.gmtime())
EPOCH = str(int(time.time()))


# ------------------------------------------------------------------ Happ / INCY JSON
def make_routing_profile(p: dict) -> dict:
    direct_ip = list(p.get("direct_ip", []))
    # Добавляем стандартные локальные подсети в direct, если профиль не пустой (JSONSUB)
    if direct_ip or p.get("direct_sites"):
        direct_ip += [
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
            "169.254.0.0/16",
            "224.0.0.0/4",
            "255.255.255.255",
        ]
        # дедупликация с сохранением порядка
        seen = set()
        dedup_ip = []
        for ip in direct_ip:
            if ip not in seen:
                seen.add(ip)
                dedup_ip.append(ip)
        direct_ip = dedup_ip

    return {
        "Name": p.get("display_name", p["name"]),
        "GlobalProxy": "true" if p.get("global_proxy", True) else "false",
        "RouteOrder": p.get("route_order", "block-proxy-direct"),
        "RemoteDNSType": DNS["remote"]["type"],
        "RemoteDNSDomain": DNS["remote"]["domain"],
        "RemoteDNSIP": DNS["remote"]["ip"],
        "RemoteDns": DNS["remote"]["ip"],
        "DomesticDNSType": DNS["domestic"]["type"],
        "DomesticDNSDomain": DNS["domestic"]["domain"],
        "DomesticDNSIP": DNS["domestic"]["ip"],
        "DomesticDns": DNS["domestic"]["ip"],
        "Geoipurl": f"{PUB['base_url']}/geoip.dat",
        "Geositeurl": f"{PUB['base_url']}/geosite.dat",
        "LastUpdated": EPOCH,
        "DnsHosts": DNS_HOSTS,
        "DirectSites": p.get("direct_sites", []),
        "DirectIp": direct_ip,
        "ProxySites": p.get("proxy_sites", []),
        "ProxyIp": p.get("proxy_ip", []),
        "BlockSites": p.get("block_sites", []),
        "BlockIp": p.get("block_ip", []),
        "DomainStrategy": p.get("domain_strategy", "IPIfNonMatch"),
        "FakeDNS": "false",
        "UseChunkFiles": "true" if p.get("use_chunk_files", True) else "false",
    }


# ------------------------------------------------------------------ Xray
def xray_config(p: dict) -> dict:
    rules = []
    if p.get("block_sites") or p.get("block_ip"):
        if p.get("block_sites"):
            rules.append({"type": "field", "domain": p["block_sites"], "outboundTag": "block"})
        if p.get("block_ip"):
            rules.append({"type": "field", "ip": p["block_ip"], "outboundTag": "block"})
    if p.get("proxy_sites"):
        rules.append({"type": "field", "domain": p["proxy_sites"], "outboundTag": "proxy"})
    if p.get("proxy_ip"):
        rules.append({"type": "field", "ip": p["proxy_ip"], "outboundTag": "proxy"})
    if p.get("direct_sites"):
        rules.append({"type": "field", "domain": p["direct_sites"], "outboundTag": "direct"})
    if p.get("direct_ip"):
        rules.append({"type": "field", "ip": p["direct_ip"], "outboundTag": "direct"})

    return {
        "dns": {
            "servers": [
                {"address": DNS["remote"]["ip"], "domains": p.get("proxy_sites", [])},
                {
                    "address": DNS["domestic"]["ip"],
                    "domains": p.get("direct_sites", []),
                    "expectIPs": p.get("direct_ip", []),
                },
                DNS["remote"]["ip"],
            ],
            "queryStrategy": "UseIPv4",
        },
        "routing": {
            "domainStrategy": p.get("domain_strategy", "IPIfNonMatch"),
            "rules": rules,
        },
    }


# ------------------------------------------------------------------ Mihomo YAML
def mihomo_config(remnawave: bool = False) -> str:
    rb = PUB["ruleset_base_url"]
    
    # Специфичные настройки для Remnawave
    if remnawave:
        remna_line = "    remnawave:\n      include-proxies: false\n"
        proxies_marker = "proxies: # LEAVE THIS LINE!\n"
        providers_block = ""
        provider_url_test = ""
    else:
        remna_line = ""
        proxies_marker = ""
        providers_block = """proxy-providers:
  prov:
    type: http
    url: "ВСТАВЬТЕ_URL_ВАШЕЙ_ПОДПИСКИ"
    path: ./provider/proxies.yaml
    interval: 86400
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
"""
        provider_url_test = "  use: [prov]\n"

    return f"""# ============================================================
# КОНФИГУРАЦИЯ MIHOMO / CLASH META
# Репозиторий: {PUB.get('base_url', '')}
# Сгенерировано: {STAMP}
# ============================================================
{providers_block}{proxies_marker}mixed-port: 7890
mode: rule
log-level: silent
allow-lan: false
ipv6: true
unified-delay: true
tcp-concurrent: true
tun:
  enable: true
  stack: system
  auto-route: true
  auto-detect-interface: true
  dns-hijack:
    - any:53
  strict-route: true
  route-exclude-address:
    - 224.0.0.0/3
    - 10.0.0.0/8
    - 127.0.0.0/8
    - 100.64.0.0/10
    - 172.16.0.0/12
    - 169.254.0.0/16
    - 192.168.0.0/16
    - 192.0.0.0/24
    - 192.0.2.0/24
    - 192.88.99.0/24
    - 198.51.100.0/24
    - 203.0.113.0/24
    - fc00::/7
    - ff00::/8
    - fe80::/10
    - ::/127
dns:
  enable: true
  ipv6: false
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    - rule-set:private-domains
  default-nameserver:
    - https://77.88.8.8/dns-query
    - https://8.8.8.8/dns-query
  proxy-server-nameserver:
    - https://77.88.8.8/dns-query
    - https://8.8.8.8/dns-query
  direct-nameserver:
    - https://77.88.8.8/dns-query
    - https://8.8.8.8/dns-query
  nameserver:
    - https://8.8.8.8/dns-query#PROXY
sniffer:
  enable: true
  override-destination: false
  parse-pure-ip: true
  sniff:
    HTTP:
      ports:
        - 80
        - 8080-8880
    TLS:
      ports:
        - 443
        - 8443
  skip-dst-address:
    - 224.0.0.0/3
    - 10.0.0.0/8
    - 127.0.0.0/8
    - 100.64.0.0/10
    - 172.16.0.0/12
    - 198.18.0.0/15
    - 169.254.0.0/16
    - 192.168.0.0/16
    - 192.0.0.0/24
    - 192.0.2.0/24
    - 192.88.99.0/24
    - 198.51.100.0/24
    - 203.0.113.0/24
    - fc00::/7
    - ff00::/8
    - fe80::/10
    - ::/127
find-process-mode: strict
profile:
  store-selected: true
  store-fake-ip: true

proxy-groups:
  - name: 🛡️ VPN
    icon: https://cdn.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color/Hijacking.png
    type: select
{remna_line}{provider_url_test}    proxies:
      - ⚡️ Авто
    include-all: true
    url: https://www.gstatic.com/generate_204

  - name: 📺 Youtube
    icon: https://cdn.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color/YouTube.png
    type: select
{remna_line}{provider_url_test}    include-all: true
    proxies:
      - 🛡️ VPN

  - name: 💬 Discord.exe
    icon: https://cdn.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color/Discord.png
    type: select
{remna_line}{provider_url_test}    include-all: true
    proxies:
      - 🛡️ VPN

  - name: 🎮 Игры
    icon: https://cdn.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color/Game.png
    type: select
{remna_line}{provider_url_test}    include-all: true
    proxies:
      - 🔓 Без VPN
      - 🛡️ VPN

  - name: ⚡️ Авто
    type: url-test
    tolerance: 150
    url: https://www.gstatic.com/generate_204
    interval: 300
{remna_line}{provider_url_test}    include-all: true
    hidden: true

  - name: PROXY
    type: select
    hidden: true
{remna_line}{provider_url_test}    proxies:
      - 🛡️ VPN

  - name: 🔓 Без VPN
    type: select
    hidden: true
{remna_line}    proxies:
      - DIRECT

  - name: ⛔ Блок
    type: select
    hidden: true
{remna_line}    proxies:
      - REJECT

  - name: ⏭️ Пропуск
    type: select
    hidden: true
{remna_line}    proxies:
      - PASS

rule-providers:
  private-domains:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-private.mrs"
    path: ./ruleset/geosite-private.mrs
    interval: 2592000
  private-ips:
    type: http
    behavior: ipcidr
    format: mrs
    url: "{rb}/mihomo/geoip-private.mrs"
    path: ./ruleset/geoip-private.mrs
    interval: 2592000
  direct-ips:
    type: http
    behavior: ipcidr
    format: mrs
    url: "{rb}/mihomo/geoip-direct.mrs"
    path: ./ruleset/geoip-direct.mrs
    interval: 86400
  category-ads:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-ads.mrs"
    path: ./ruleset/geosite-ads.mrs
    interval: 86400
  win-spy:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-win-spy.mrs"
    path: ./ruleset/geosite-win-spy.mrs
    interval: 86400
  torrent-domains:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-torrent.mrs"
    path: ./ruleset/geosite-torrent.mrs
    interval: 86400
  google-play:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-google-play.mrs"
    path: ./ruleset/geosite-google-play.mrs
    interval: 86400
  twitch-ads:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-twitch-ads.mrs"
    path: ./ruleset/geosite-twitch-ads.mrs
    interval: 86400
  youtube:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-youtube.mrs"
    path: ./ruleset/geosite-youtube.mrs
    interval: 86400
  telegram:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-telegram.mrs"
    path: ./ruleset/geosite-telegram.mrs
    interval: 86400
  discord:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-discord.mrs"
    path: ./ruleset/geosite-discord.mrs
    interval: 86400
  github:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-github.mrs"
    path: ./ruleset/geosite-github.mrs
    interval: 86400
  openai:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-openai.mrs"
    path: ./ruleset/geosite-openai.mrs
    interval: 86400
  games:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-games.mrs"
    path: ./ruleset/geosite-games.mrs
    interval: 86400
  twitch:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-twitch.mrs"
    path: ./ruleset/geosite-twitch.mrs
    interval: 86400
  microsoft:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-microsoft.mrs"
    path: ./ruleset/geosite-microsoft.mrs
    interval: 86400
  apple:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-apple.mrs"
    path: ./ruleset/geosite-apple.mrs
    interval: 86400
  pinterest:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-pinterest.mrs"
    path: ./ruleset/geosite-pinterest.mrs
    interval: 86400
  category-ru:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-ru-services.mrs"
    path: ./ruleset/geosite-ru-services.mrs
    interval: 86400
  banks-ru:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-banks-ru.mrs"
    path: ./ruleset/geosite-banks-ru.mrs
    interval: 86400
  whitelist:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-whitelist.mrs"
    path: ./ruleset/geosite-whitelist.mrs
    interval: 86400
  my-proxy:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-my-proxy.mrs"
    path: ./ruleset/geosite-my-proxy.mrs
    interval: 86400
  my-direct:
    type: http
    behavior: domain
    format: mrs
    url: "{rb}/mihomo/geosite-my-direct.mrs"
    path: ./ruleset/geosite-my-direct.mrs
    interval: 86400

rules:
  # --- Системные / приватные адреса ---
  - RULE-SET,private-ips,DIRECT,no-resolve
  - IP-CIDR,::/0,REJECT-DROP,no-resolve
  - AND,((NETWORK,UDP),(DST-PORT,443)),REJECT-DROP
  - RULE-SET,private-domains,DIRECT

  # --- Блокировки (реклама, телеметрия) ---
  - RULE-SET,category-ads,REJECT-DROP
  - RULE-SET,win-spy,REJECT-DROP
  - RULE-SET,torrent-domains,DIRECT

  # --- Сервисы через PROXY ---
  - RULE-SET,google-play,PROXY
  - RULE-SET,twitch-ads,PROXY
  - RULE-SET,youtube,📺 Youtube
  - RULE-SET,telegram,PROXY
  - RULE-SET,discord,💬 Discord.exe
  - RULE-SET,github,PROXY
  - RULE-SET,openai,PROXY
  - RULE-SET,my-proxy,PROXY

  # --- Игровые сервисы ---
  - RULE-SET,games,🎮 Игры

  # --- Сервисы в DIRECT ---
  - RULE-SET,twitch,DIRECT
  - RULE-SET,microsoft,DIRECT
  - RULE-SET,apple,DIRECT
  - RULE-SET,pinterest,DIRECT
  - RULE-SET,category-ru,DIRECT
  - RULE-SET,banks-ru,DIRECT
  - RULE-SET,whitelist,DIRECT
  - RULE-SET,my-direct,DIRECT

  # --- Приложения по имени процесса ---
  - PROCESS-NAME-REGEX,discord,💬 Discord.exe
  - PROCESS-NAME-REGEX,vesktop,💬 Discord.exe

  # --- IP-адреса → DIRECT ---
  - RULE-SET,direct-ips,DIRECT

  # --- Всё остальное → PROXY ---
  - MATCH,PROXY
"""


def main() -> None:
    # Директории в dist/
    for sub in ("happ", "incy", "xray", "mihomo"):
        (DIST / sub).mkdir(parents=True, exist_ok=True)

    # Директории в корне репозитория (как в roscomvpn-routing)
    for folder in ("HAPP", "INCY", "MIHOMO"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)

    for p in CFG["profiles"]:
        name = p["name"]
        prof = make_routing_profile(p)
        compact_json = json.dumps(prof, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        formatted_json = json.dumps(prof, ensure_ascii=False, indent=2)

        # 1. HAPP (happ://routing/onadd/<b64>)
        happ_b64 = base64.b64encode(compact_json).decode("utf-8")
        happ_link = f"happ://routing/onadd/{happ_b64}\n"
        
        (DIST / "happ" / f"{name}.json").write_text(formatted_json, encoding="utf-8")
        (DIST / "happ" / f"{name}.link").write_text(happ_link, encoding="utf-8")
        (ROOT / "HAPP" / f"{name}.JSON").write_text(formatted_json, encoding="utf-8")
        (ROOT / "HAPP" / f"{name}.DEEPLINK").write_text(happ_link, encoding="utf-8")

        # 2. INCY (incy://routing/onadd/<b64>)
        incy_b64 = base64.b64encode(compact_json).decode("utf-8")
        incy_link = f"incy://routing/onadd/{incy_b64}\n"
        
        (DIST / "incy" / f"{name}.json").write_text(formatted_json, encoding="utf-8")
        (DIST / "incy" / f"{name}.link").write_text(incy_link, encoding="utf-8")
        (ROOT / "INCY" / f"{name}.JSON").write_text(formatted_json, encoding="utf-8")
        (ROOT / "INCY" / f"{name}.DEEPLINK").write_text(incy_link, encoding="utf-8")

        # 3. Xray
        (DIST / "xray" / f"{name}.json").write_text(
            json.dumps(xray_config(p), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # 4. Mihomo
    mihomo_default = mihomo_config(remnawave=False)
    mihomo_remnawave = mihomo_config(remnawave=True)

    (ROOT / "MIHOMO" / "default.yaml").write_text(mihomo_default, encoding="utf-8")
    (ROOT / "MIHOMO" / "template_remnawave.yaml").write_text(mihomo_remnawave, encoding="utf-8")
    (DIST / "mihomo" / "default.yaml").write_text(mihomo_default, encoding="utf-8")
    (DIST / "mihomo" / "template_remnawave.yaml").write_text(mihomo_remnawave, encoding="utf-8")

    (DIST / "version.txt").write_text(STAMP + "\n", encoding="utf-8")
    print(f"rendered {len(CFG['profiles'])} profiles for HAPP, INCY, MIHOMO, version {STAMP}")


if __name__ == "__main__":
    main()
