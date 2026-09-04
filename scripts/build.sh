#!/usr/bin/env bash
# Полная сборка: geosite.dat, geoip.dat, рулсеты для mihomo (.mrs) и sing-box (.srs),
# готовые конфиги роутинга.
#
# Требуется: go >= 1.22, git, curl, python3
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source scripts/lists.sh

TOOLS="$ROOT/.tools"
DIST="$ROOT/dist"
export GOBIN="$TOOLS/bin"
export PATH="$GOBIN:$TOOLS:$PATH"

SING_BOX_VERSION="${SING_BOX_VERSION:-1.11.15}"
MIHOMO_VERSION="${MIHOMO_VERSION:-v1.19.14}"

mkdir -p "$TOOLS/bin" "$DIST"
rm -rf "$DIST"/* 2>/dev/null || true

log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }

# ---------------------------------------------------------------- 1. тулчейн
install_tools() {
  if [ ! -x "$GOBIN/domain-list-community" ]; then
    log "устанавливаю компилятор geosite (v2fly/domain-list-community)"
    go install github.com/v2fly/domain-list-community@latest
  fi
  if [ ! -x "$GOBIN/geoip" ]; then
    log "устанавливаю конвертер geoip (Loyalsoldier/geoip)"
    go install github.com/Loyalsoldier/geoip@latest
  fi
  if [ ! -x "$TOOLS/sing-box" ]; then
    log "качаю sing-box $SING_BOX_VERSION"
    curl -sSL "https://github.com/SagerNet/sing-box/releases/download/v${SING_BOX_VERSION}/sing-box-${SING_BOX_VERSION}-linux-amd64.tar.gz" \
      | tar -xz -C "$TOOLS" --strip-components=1 "sing-box-${SING_BOX_VERSION}-linux-amd64/sing-box"
  fi
  if [ ! -x "$TOOLS/mihomo" ]; then
    log "качаю mihomo $MIHOMO_VERSION"
    curl -sSL -o "$TOOLS/mihomo.gz" \
      "https://github.com/MetaCubeX/mihomo/releases/download/${MIHOMO_VERSION}/mihomo-linux-amd64-${MIHOMO_VERSION}.gz"
    gunzip -f "$TOOLS/mihomo.gz"
    chmod +x "$TOOLS/mihomo"
  fi
}

# ---------------------------------------------------------------- 2. geosite
build_geosite() {
  log "собираю geosite.dat из data/"
  mkdir -p "$DIST/geosite-text"
  domain-list-community \
    --datapath="$ROOT/data" \
    --outputdir="$DIST" \
    --outputname=geosite.dat \
    --exportlists="$GEOSITE_LISTS"
  # экспортированные плоские списки кладём отдельно
  for name in ${GEOSITE_LISTS//,/ }; do
    [ -f "$DIST/$name.txt" ] && mv "$DIST/$name.txt" "$DIST/geosite-text/$name.txt"
  done
}

# ------------------------------------------------- 3. рулсеты доменов mrs/srs
build_domain_rulesets() {
  log "конвертирую доменные списки в .srs (sing-box) и .mrs (mihomo)"
  mkdir -p "$DIST/sing-box" "$DIST/mihomo" "$DIST/.tmp"
  python3 scripts/domain_rulesets.py "$DIST/geosite-text" "$DIST/.tmp"
  for f in "$DIST/.tmp"/*.json; do
    name="$(basename "$f" .json)"
    sing-box rule-set compile --output "$DIST/sing-box/geosite-$name.srs" "$f"
  done
  for f in "$DIST/.tmp"/*.list; do
    name="$(basename "$f" .list)"
    mihomo convert-ruleset domain text "$f" "$DIST/mihomo/geosite-$name.mrs"
  done
  rm -rf "$DIST/.tmp"
}

# ----------------------------------------------------------------- 4. geoip
build_geoip() {
  log "собираю geoip.dat и IP-рулсеты"
  geoip convert -c "$ROOT/geoip.config.json"
}

# -------------------------------------------------------- 5. конфиги роутинга
render_configs() {
  log "рендерю конфиги роутинга"
  python3 scripts/render_configs.py
  # Хеши sha256 для клиентов автообновления
  if [ -f "$DIST/geoip.dat" ]; then
    sha256sum "$DIST/geoip.dat" | awk '{print $1}' > "$DIST/geoip.dat.sha256"
  fi
  if [ -f "$DIST/geosite.dat" ]; then
    sha256sum "$DIST/geosite.dat" | awk '{print $1}' > "$DIST/geosite.dat.sha256"
  fi
  # Архивы правил для удобного скачивания
  if [ -d "$DIST/mihomo" ]; then
    tar -czf "$DIST/mihomo.tar.gz" -C "$DIST" mihomo
  fi
  if [ -d "$DIST/sing-box" ]; then
    tar -czf "$DIST/sing-box.tar.gz" -C "$DIST" sing-box
  fi
}

install_tools
build_geosite
build_domain_rulesets
build_geoip
render_configs

log "готово, всё в dist/"
find "$DIST" -maxdepth 2 -type f | sort | sed 's|^|    |'
