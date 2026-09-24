#!/usr/bin/env python3
"""Remove stale peninsula Yeelight registry entries after hardware replacement."""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("/config/.storage")
OLD_ENTRY = "01JYMEP31217V12B2Y8BRQMDC5"
OLD_DEVICE = "6be59ba7775d81b2d9794c9971f90167"
OLD_UNIQUE = "0x000000000456ac00"


def main() -> int:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for fname in ("core.config_entries", "core.device_registry", "core.entity_registry"):
        src = BASE / fname
        shutil.copy2(src, BASE / f"{fname}.bak_{ts}_peninsula_fix")

    with (BASE / "core.config_entries").open() as f:
        ce = json.load(f)
    before = len(ce["data"]["entries"])
    ce["data"]["entries"] = [e for e in ce["data"]["entries"] if e["entry_id"] != OLD_ENTRY]
    with (BASE / "core.config_entries").open("w") as f:
        json.dump(ce, f, indent=2)
    print(f"config_entries: {before} -> {len(ce['data']['entries'])}")

    with (BASE / "core.device_registry").open() as f:
        dr = json.load(f)
    before = len(dr["data"]["devices"])
    dr["data"]["devices"] = [d for d in dr["data"]["devices"] if d["id"] != OLD_DEVICE]
    with (BASE / "core.device_registry").open("w") as f:
        json.dump(dr, f, indent=2)
    print(f"devices: {before} -> {len(dr['data']['devices'])}")

    with (BASE / "core.entity_registry").open() as f:
        er = json.load(f)
    before = len(er["data"]["entities"])
    er["data"]["entities"] = [
        e
        for e in er["data"]["entities"]
        if not (e.get("config_entry_id") == OLD_ENTRY and e.get("unique_id") == OLD_UNIQUE)
    ]
    with (BASE / "core.entity_registry").open("w") as f:
        json.dump(er, f, indent=2)
    print(f"entities: {before} -> {len(er['data']['entities'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
