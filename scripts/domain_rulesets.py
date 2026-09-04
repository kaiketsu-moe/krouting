#!/usr/bin/env python3
"""Плоские geosite-списки -> исходники рулсетов для sing-box и mihomo.

Вход: каталог с *.txt, экспортированными domain-list-community
      (строки вида `domain:x`, `full:x`, `keyword:x`, `regexp:x`).
Выход: <name>.json  — sing-box rule-set source (компилируется в .srs)
       <name>.list  — mihomo text ruleset behavior=domain (компилируется в .mrs)
"""
import json
import pathlib
import sys


def parse(line: str):
    line = line.split("#", 1)[0].strip()
    if not line:
        return None
    # атрибуты в экспорте выглядят как `domain:apple.com:@push`
    line = line.split(":@", 1)[0].split(" @", 1)[0].strip().rstrip(":")
    if ":" in line:
        kind, value = line.split(":", 1)
        kind = kind.strip().lower()
    else:
        kind, value = "domain", line
    value = value.strip()
    if not value or kind not in ("domain", "full", "keyword", "regexp"):
        return None
    return kind, value


def main() -> int:
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)

    for path in sorted(src.glob("*.txt")):
        suffix, exact, keyword, regexp = [], [], [], []
        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = parse(line)
            if not parsed:
                continue
            kind, value = parsed
            if kind == "domain":
                # domain: сам домен + все поддомены
                exact.append(value)
                suffix.append("." + value)
            elif kind == "full":
                exact.append(value)
            elif kind == "keyword":
                keyword.append(value)
            elif kind == "regexp":
                regexp.append(value)

        rule = {}
        if exact:
            rule["domain"] = sorted(set(exact))
        if suffix:
            rule["domain_suffix"] = sorted(set(suffix))
        if keyword:
            rule["domain_keyword"] = sorted(set(keyword))
        if regexp:
            rule["domain_regex"] = sorted(set(regexp))
        if not rule:
            continue

        (dst / f"{path.stem}.json").write_text(
            json.dumps({"version": 3, "rules": [rule]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        lines = []
        lines += [f"+.{d}" for d in sorted(set(x.lstrip('.') for x in suffix))]
        lines += sorted(set(exact))
        lines += [f"*{k}*" for k in sorted(set(keyword))]
        (dst / f"{path.stem}.list").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
