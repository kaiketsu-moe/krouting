.PHONY: all build clean configs check
all: build

build:
	bash scripts/build.sh

configs:
	python3 scripts/render_configs.py

check:
	python3 - <<'PY'
import json,pathlib
for f in ("profiles.json","geoip.config.json"):
    json.loads(pathlib.Path(f).read_text())
print("configs ok")
PY

clean:
	rm -rf dist .tools
