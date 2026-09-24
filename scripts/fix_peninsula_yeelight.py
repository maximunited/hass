#!/usr/bin/env python3
"""Remove stale peninsula Yeelight registry entries after hardware replacement.

DANGEROUS: rewrites Home Assistant `.storage` registries. Stop HA first
(`docker stop homeassistant` or equivalent). Default is dry-run; pass
`--apply` to write (still creates timestamped `.bak_*` copies).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("/config/.storage")
OLD_ENTRY = "01JYMEP31217V12B2Y8BRQMDC5"
OLD_DEVICE = "6be59ba7775d81b2d9794c9971f90167"
OLD_UNIQUE = "0x000000000456ac00"
STORAGE_FILES = (
    "core.config_entries",
    "core.device_registry",
    "core.entity_registry",
)


def _load(name: str) -> dict:
    with (BASE / name).open() as f:
        return json.load(f)


def _plan(ce: dict, dr: dict, er: dict) -> tuple[list, list, list]:
    entries = [e for e in ce["data"]["entries"] if e["entry_id"] == OLD_ENTRY]
    devices = [d for d in dr["data"]["devices"] if d["id"] == OLD_DEVICE]
    entities = [
        e
        for e in er["data"]["entities"]
        if e.get("config_entry_id") == OLD_ENTRY and e.get("unique_id") == OLD_UNIQUE
    ]
    return entries, devices, entities


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default: dry-run only)",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=BASE,
        help=f"Path to .storage (default: {BASE})",
    )
    args = parser.parse_args()
    global BASE
    BASE = args.base

    for fname in STORAGE_FILES:
        if not (BASE / fname).is_file():
            print(f"error: missing {BASE / fname}", file=sys.stderr)
            return 1

    ce, dr, er = (
        _load("core.config_entries"),
        _load("core.device_registry"),
        _load("core.entity_registry"),
    )
    entries, devices, entities = _plan(ce, dr, er)

    print(f"Would remove {len(entries)} config entry/ies matching {OLD_ENTRY}")
    print(f"Would remove {len(devices)} device(s) matching {OLD_DEVICE}")
    print(f"Would remove {len(entities)} entit(y/ies) matching {OLD_UNIQUE}")
    for e in entries:
        print(f"  entry: {e.get('title')} ({e.get('domain')})")
    for d in devices:
        print(f"  device: {d.get('name_by_user') or d.get('name')} ({d['id']})")
    for e in entities:
        print(f"  entity: {e.get('entity_id')} unique_id={e.get('unique_id')}")

    if not entries and not devices and not entities:
        print("Nothing to do (IDs already absent).")
        return 0

    if not args.apply:
        print("Dry-run only. Re-run with --apply after stopping Home Assistant.")
        return 0

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for fname in STORAGE_FILES:
        src = BASE / fname
        shutil.copy2(src, BASE / f"{fname}.bak_{ts}_peninsula_fix")

    ce["data"]["entries"] = [e for e in ce["data"]["entries"] if e["entry_id"] != OLD_ENTRY]
    with (BASE / "core.config_entries").open("w") as f:
        json.dump(ce, f, indent=2)
    print(f"config_entries written ({len(ce['data']['entries'])} remain)")

    dr["data"]["devices"] = [d for d in dr["data"]["devices"] if d["id"] != OLD_DEVICE]
    with (BASE / "core.device_registry").open("w") as f:
        json.dump(dr, f, indent=2)
    print(f"devices written ({len(dr['data']['devices'])} remain)")

    er["data"]["entities"] = [
        e
        for e in er["data"]["entities"]
        if not (e.get("config_entry_id") == OLD_ENTRY and e.get("unique_id") == OLD_UNIQUE)
    ]
    with (BASE / "core.entity_registry").open("w") as f:
        json.dump(er, f, indent=2)
    print(f"entities written ({len(er['data']['entities'])} remain)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
