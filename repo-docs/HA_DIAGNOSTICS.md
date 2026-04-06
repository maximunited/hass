# Home Assistant diagnostics and log findings

## Location and discovery

This file is **`repo-docs/HA_DIAGNOSTICS.md`** (this folder is **this git repo’s** notes—not official Home Assistant documentation). The [README](../README.md) points here. **Cursor:** project rule **`.cursor/rules/homeassistant-repo-docs.mdc`** (`alwaysApply: true`) instructs the agent to read this file when work touches HA config, integrations, or troubleshooting. You can still attach **`@repo-docs/HA_DIAGNOSTICS.md`** if you want it in context explicitly.

Persistent notes from log analysis and live-instance checks. **Update this file** when you fix integrations or run a new investigation so future sessions (human or AI) do not start from zero.

## How to re-check

- **Files:** `home-assistant.log`, `home-assistant.log.1` in this repo (or on the HA host).
- **MCP (Cursor):** `user-hass-mcp` — e.g. `get_error_log`, `search_entities_tool`, `get_entity`, `get_version`.
- **In HA UI:** Settings → System → Logs; Developer tools → States.

---

## Snapshot: 2026-04-05 (HA 2026.4.1)

### MCP error log aggregates (same day)

| Metric | Value | Note |
| ------ | ----- | ---- |
| ERROR count | ~798 | Full log slice returned by MCP |
| `proxmoxve` mentions | ~1512 | Dominant integration noise |
| `KeyError` mentions | ~751 | Aligns with Proxmox node sensor failures |
| `jellyfin.local` | 0 | Not appearing in that log window |
| `imou_life` | ~39 | Intermittent / lower volume |
| `iec` | ~1 | Not prioritized (see below) |

### Proxmox VE

**Symptom:** `KeyError: 'cpu'`, `'mem'`, `'disk'`, etc. in core `proxmoxve` when computing `sensor.nuc_*` states; repeating **Task exception was never retrieved** on coordinator refresh.

**Live state (MCP):** `sensor.nuc_cpu_usage`, disk/memory/uptime sensors **`unavailable`**; `sensor.nuc_cpu_usage` had **`restored: true`** (registry ghost after failed platform setup). Buttons/binary sensors for the same host may still appear **on** — integration partially connected, **node metrics not**.

**Root cause (typical):** Node name in HA does not match **Datacenter → Nodes** in Proxmox (e.g. `pve` vs host nickname), wrong device type (VM/LXC vs node), or API user lacks permission to read **node status**.

**Config in repo:** `proxmoxve:` block is **commented** in `configuration.yaml`; the live integration is almost certainly **UI-only** (Settings → Devices & services). `secrets.yaml` still holds `proxmox_*` for optional YAML use — editing secrets **does not** change UI entries.

**Fix (operational):**

1. Proxmox UI: **Datacenter → Nodes** — copy the **exact** node id.
2. HA: **Settings → Devices & services → Proxmox VE → Configure** — set that node; add guests as **QEMU/LXC**, not a mislabeled node.
3. Proxmox: ensure the HA API user/token role can read node status.
4. After fix: consider removing broken `sensor.nuc_*` from **Entity registry** so they recreate cleanly.

**In-repo pointers:** Comments above the commented `proxmoxve` block in `configuration.yaml`.

### Low battery automation

**Symptom:** `Template error: float got invalid input 'Rechargeable'` — entity_ids containing `battery` included **non-numeric** sensors (e.g. battery technology).

**Fix applied in repo:** Automation `low_battery_check_all_sensors` in `automations.yaml` — require `state.state | is_number` and only treat **0–100** as percentage before comparing to 20.

### Jellyfin

**Historical (`.log.1`):** `Failed to resolve 'jellyfin.local'` from the Jellyfin integration.

**MCP snapshot:** `sensor.jellyfin_active_clients` and Docker monitor entities for Jellyfin **healthy**; no `jellyfin.local` hits in the analyzed MCP log window.

**If it regresses:** Use **IP** or fix **DNS/mDNS** for the HA container; see comment in `configuration.yaml` near Proxmox block.

### Imou Life (custom / HACS)

**Symptom:** `Imou exception` (sometimes empty), occasionally `OP1001: Operation failed`, slow platform setup warnings.

**MCP snapshot:** Garage Imou entities (camera, battery, online, etc.) **working**; log noise remains moderate vs Proxmox.

**If needed:** Update integration via HACS; re-check app credentials and cloud reachability. Comment in `configuration.yaml` near Proxmox block.

### IEC (Israel Electric — HACS)

**Status:** Explicitly **out of scope** for the 2026-04-05 pass. Log reference: `(Code 400): Bad Request` and setup follow-on errors in older log. Revisit with credentials / integration changelog when desired.

---

## Informational noise (usually ignore)

- Startup **WARNING** “custom integration … has not been tested” for HACS components — expected.
- For crashes, also check `home-assistant.log.fault` on the host.

---

## Pikud Oref lighting (2026-04-06)

**Symptom:** After pre-alert → timeout restore → safe (`sensor.oref_alert` ok), a second `timer.pikud_scene_timeout` run did not restore lights because `input_text.pikud_original_snapshot_scene` was already cleared on the first timeout; safe state had restarted the same timer with nothing to restore.

**Fix in repo:** `pikud_safe_start` no longer starts `timer.pikud_scene_timeout`. On safe it **cancels** that timer (so a long pre-alert countdown cannot fire after safe), applies `scene.safe_pikud`, clears the snapshot text, and turns **off** `input_boolean.pikud_scene_active` so ambient / pending logic can run. Only the pre-alert path still drives the 20-minute cap and `pikud_timeout_restore_original`.

---

## Changelog

| Date | Change |
| ---- | ------ |
| 2026-04-06 | Pikud: decouple safe state from `timer.pikud_scene_timeout` / restore automation (see section above). |
| 2026-04-05 | Initial doc: log + MCP findings; battery template fix; config comments; IEC deferred. |
| 2026-04-05 | Moved from repo root to `docs/HA_DIAGNOSTICS.md`; added discovery note for AI tools. |
| 2026-04-05 | Renamed folder `docs/` → `repo-docs/` to avoid confusion with official HA documentation. |
| 2026-04-05 | Added Cursor rule `.cursor/rules/homeassistant-repo-docs.mdc` to load this doc for HA-related tasks. |
