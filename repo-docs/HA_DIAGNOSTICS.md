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

## Pikud Oref lighting (2026-04-06, updated 2026-04-07)

**Symptom (first fix):** After pre-alert → timeout restore → safe (`sensor.oref_alert` ok), a second `timer.pikud_scene_timeout` run did not restore lights because `input_text.pikud_original_snapshot_scene` was already cleared on the first timeout; safe had restarted the same timer with nothing to restore.

**Fix:** `pikud_safe_start` no longer starts `timer.pikud_scene_timeout`. On safe it **cancels** that timer so a late `timer.finished` cannot fire after safe.

**Symptom (2026-04-07):** Cancel alone meant **no** `timer.finished` event if ok arrived before the 20-minute timer completed, so `pikud_timeout_restore_original` never ran and lights were not restored (snapshot was cleared without `scene.turn_on`).

**Fix:** `pikud_safe_start` now mirrors the timeout restore automation after cancel: if the snapshot entity id is non-empty and valid, `scene.turn_on` that snapshot; clear `input_text.pikud_original_snapshot_scene`; turn **off** `input_boolean.pikud_scene_active`; run the same `pikud_ambient_pending` + `group.household` home branch as the timer automation; then `scene.safe_pikud`. The timer-based automation remains for pre-alert windows that **expire** without ok.

**MCP / recorder check (2026-04-07):** `user-hass-mcp` has no automation trace API; use `list_automations` (`last_triggered`), `get_history`, `get_entity`. For one real event (pre-alert ~15:37 UTC, alert ~15:41, ok ~15:52): **Pikud Oref - Restore original lights on timeout** did not run (`last_triggered` still previous day) because **timer was cancelled** before 20 minutes. `input_text.pikud_original_snapshot_scene` held `scene.pikud_original_lights` until safe cleared it; **`scene.pikud_original_lights` `last_changed` at the same second as safe** indicates `scene.turn_on` for the snapshot ran, then **`scene.safe_pikud` immediately replaces** those levels/colors with the green “safe” scene — so “originals” are not what you see after safe unless you drop or delay `scene.safe_pikud`.

**`input_boolean.pikud_timeout_restore` (2026-04-08):** When **off**, pre-alert does **not** start `timer.pikud_scene_timeout`, and the timeout automation does **not** call `scene.turn_on` on the snapshot (it still clears the snapshot text and turns off `input_boolean.pikud_scene_active`). **Enter safe** still cancels the 20m timer; pre-Pikud restore after ok is handled by **post-safe** delay, not this toggle. Default **on** preserves 20m timeout behavior.

**Post-safe delay (2026-04-08):** After **ok**, **Enter safe** applies `scene.safe_pikud` and starts **`timer.pikud_safe_post_restore`** (3m30s); **`pikud_post_safe_restore_original`** then restores the pre-Pikud snapshot and runs ambient cleanup. Pre-alert **from `ok`** re-snapshots even if `pikud_scene_active` is still on. See [`repo-docs/automations-pikud-oref.md`](automations-pikud-oref.md).

---

## Snapshot: 2026-08-05 (repairs + current log)

Current `home-assistant.log` (~since restart 19:45): **~84 ERROR**, **~40 WARNING**. Dominant ERROR source is **CityMind water meter** API **HTTP 429** (~57 lines), not the UI repairs.

### UI repairs (4)

| Repair | Severity | Meaning / action |
| ------ | -------- | ---------------- |
| PlayStation Network `maxim_united` | Error | Auth expired — re-auth in Settings → Devices & services → PlayStation Network (or remove entry). Logged at startup as auth failure. |
| Tuya `gg-100686459991970018445` | Error | Auth expired — re-auth Tuya (or remove). YAML `tuya:` already commented; live entry is UI. |
| Battery Notes `shellyplussmoke-a0a3b3b9c4e4` | Issue | Device link missing for smoke alarm battery note. Device exists live (`sensor.shellyplussmoke_…_battery` = 100%). Open repair → select/link device. |
| HTTP YAML ignored after migration | Warning | **Fixed 2026-08-06:** `.storage/http` stable already had `use_x_forwarded_for=true` and `trusted_proxies=[172.19.0.0/16, 192.168.1.0/24]`; removed YAML `http:` block from `configuration.yaml` and restarted. |

### Other log issues (not in Repairs UI)

| Issue | Priority | Note |
| ----- | -------- | ---- |
| CityMind water meter 429 | High noise | Continuous rate-limit; poll quieter or disable until API cools. |
| Script `remove_completed_duplicates_from_todo_list` | Medium | ~20 errors: stale todo item uids (“Unable to find to-do list item”). |
| Shelly “Sofa light” fetch errors | Low | Intermittent; `light.sofa_light` / `switch.sofa_light` currently **off** (reachable). |
| MQTT connection refused (startup) | Check | One ERROR at boot; no further MQTT errors in this log window — confirm broker came up after HA. |
| Palgate relay mode 400 | Low | `device not found` for serial `0549847494`. |
| DLNA SSDP / TCL TV | Noise | One-shot callback exception at discovery. |
| Pushbullet sensors attribute size | Warning | `sensor.pushbullet_*` attrs >16KB — not stored in DB. |
| HACS `custom-cards/bar-card` removed | Warning | Unmaintained; consider uninstall. |

Proxmox/Jellyfin noise from Apr snapshot **not** dominant in this log window.

---

## Changelog

| Date | Change |
| ---- | ------ |
| 2026-08-06 | Telegram `migrate_notify`: removed YAML `notify` telegram platform; automations now use `notify.send_message` → `notify.telegram_bot_1357375595_1168033187`. bar-card: HACS installed + resource loaded, not used in any dashboard. |
| 2026-08-06 | HTTP migration complete: verified UI/storage proxies match YAML; removed `http:` from `configuration.yaml`; HA restart. Tuya: only VT002 (Mamad) + 5 sensors, all unavailable pending re-auth. |
| 2026-08-05 | Repairs triage (PSN, Tuya, Battery Notes smoke, HTTP YAML migrate) + log snapshot (CityMind 429 dominant). |
| 2026-04-08 | Pikud: post-safe `timer.pikud_safe_post_restore` (3m30s) + `pikud_post_safe_restore_original`; `timer.yaml` + pre-alert from-ok snapshot. |
| 2026-04-08 | Pikud: `input_boolean.pikud_timeout_restore` gates 20 min timer start and timeout scene restore. |
| 2026-04-07 | Pikud: MCP/recorder note — timeout automation idle when ok early; safe restores snapshot then `safe_pikud` overwrites visually. |
| 2026-04-07 | Pikud safe: after `timer.cancel`, run same restore/cleanup/ambient logic as timeout automation, then `scene.safe_pikud`. |
| 2026-04-06 | Pikud: decouple safe state from `timer.pikud_scene_timeout` / restore automation (see section above). |
| 2026-04-05 | Initial doc: log + MCP findings; battery template fix; config comments; IEC deferred. |
| 2026-04-05 | Moved from repo root to `docs/HA_DIAGNOSTICS.md`; added discovery note for AI tools. |
| 2026-04-05 | Renamed folder `docs/` → `repo-docs/` to avoid confusion with official HA documentation. |
| 2026-04-05 | Added Cursor rule `.cursor/rules/homeassistant-repo-docs.mdc` to load this doc for HA-related tasks. |
