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

## Main media scripts / IR (2026-08-15)

**Symptom:** `input_select.main_media` does not match the living-room stack. Helper restored as **Jellyfin**; Marantz `source` is **HOT**; TCL Android TV Remote app is `com.tcl.tv`. Sync automation `main_media_sync_helper_from_devices` last ran ~12:53 local and logged `Invalid option: Unknown`.

**Detection bugs:**

- HOT is inferred when AVR `HOT` **or** HomeKit `media_player.85c855_television` source `Cable`.
- `media_player.tcl_tv_2` is a **Jellyfin client session**, not a second TV. `media_player.tcl_tv` was already taken by Android TV Remote, so HA appended `_2`. Jellyfin players go unavailable when the app is idle — do not use them for activity.
- Unmatched states write option **Unknown**, which is not in the helper. Best-guess should accept AVR `HOT` alone as cable.
- Scripts still target missing `media_player.lg_tv`. Playstation script selects AVR source **PlayStation** — PS5 is **TV HDMI 1**; AVR should stay **TV Audio** except HOT (TV HDMI 4 Cable).

**IR:** SmartIR `6900.json` (HOT MagicHD on Broadlink `192.168.1.15`) has power and digits; `script.main_media_hot` never calls `media_player.living_room_hot`. `irCommands.json` is mostly unused (old LG TV, duplicate keys, TV Box Up packet ≠ `templates/tv_box.yaml`). No Netflix / YouTube / Stremio scripts. PS5 entity `media_player.playstation_5` has `supported_features: 0` (not used by scripts).

**Improve:** WoL for PS5; hide duplicate Cast/DLNA/`tcl_tv_2` players.

**YAML leftover:** `input_select.main_media_status` unquoted `Off` → live option **False**. Real helper is UI `input_select.main_media` (not in git).

**Loop:** Sync (if it succeeded) and script-end `input_select.select_option` would re-trigger `Main Media - Run script from helper`.

**Fix applied (2026-08-15):** `script.main_media_set` (AVR TV Audio except HOT; HDMI Cable/Playstation via HomeKit when available; SmartIR HOT box; PS5 WoL). `sensor.main_media_detected` best-guess, never Unknown. Sync copies the sensor and skips while the switcher runs. Run-script ignores `parent_id` writes. Helper options include Stremio / Netflix / YouTube.

**HOT box re-trigger bug (2026-08-15 evening):** After a failed streaming test, HomeKit **Cable** kept `sensor.main_media_detected` at **HOT** while AVR was **TV Audio** and the HOT box was off. Sync wrote **HOT** onto the helper; run-script could re-run the HOT branch. **Fix:** `input_boolean.main_media_sync_guard` wraps sync writes; run-script requires guard off and blocks **streaming → HOT** transitions. **Sensor fix (~18:15):** ignore HomeKit Cable when AVR is **TV Audio**.

**Chaotic Jellyfin test (~18:10):** Old 6-step shared fallback re-ran `play_media`/`turn_on` with `market://` and app URLs across activities; stale katniss query **“funny shows”** (not in repo) ran when `SEARCH` opened without clearing; wrong apps (YouTube/Netflix) from URL fallbacks or search results. **Fix (~18:20):** removed all search/text fallback; Apps-row DPAD navigation with `app_dpad_down` / `app_dpad_right` calibration fields.

**Live test + follow-up (2026-08-15 evening):**

- **Android TV Remote:** `HOME` exits HDMI (`com.tcl.tv` → launcher). **URL `play_media` works** (`https://www.youtube.com`, `https://www.netflix.com/title`); **app package `play_media` fails silently** on TCL Google TV. Package apps use Apps-row **DPAD** fallback only (no katniss search — voice input incompatible with `text:`).
- **Netflix (2026-08-15 ~18:24):** **PASS** — user confirmed Netflix on TV via URL launch (`https://www.netflix.com/title`). No script changes needed.
- **HOT box SmartIR toggle (2026-08-15 ~18:24):** Streaming path had **duplicate** `turn_off` on `media_player.living_room_hot` (IR toggle could flash box on when already off). **Fix:** single conditional `turn_off` only when state `on`; HOT path `turn_on` only when state `off`.
- **Jellyfin test (2026-08-15 ~18:24):** Ran `script.main_media_jellyfin` once with `app_dpad_down: 2`, `app_dpad_right: 0` (ALL_APPS row). MCP after run: AVR **TV Audio**, HOT **off**, TCL **on** (`app_id` launcher — package `play_media` silent, DPAD fallback expected). Helper briefly **Jellyfin** then sync wrote **Netflix** (stale `sensor.main_media_detected` from prior Netflix test). **Pending user visual:** ALL_APPS drawer opened? Jellyfin launched? HOT stayed off?
- **Plex test (2026-08-15 ~18:28):** User on Plex manually; baseline `app_id` **com.plexapp.android**. HOME → launcher OK. Restore: package `play_media`, `remote.turn_on` (package + URL), URL `play_media` — all **silent fail** on launcher. `script.main_media_plex` (DPAD down:1 right:0) — still launcher. Manual ALL_APPS + DOWN×2 + ENTER → **com.tcl.tv** (wrong tile). HOT **off** throughout. Plex URL does **not** work (unlike Netflix/YouTube). Full snapshot: [PLEX_DEBUG_SNAPSHOT_2026-08-15.md](PLEX_DEBUG_SNAPSHOT_2026-08-15.md). **Pending:** DPAD tile calibration + user visual.
- **Plex DPAD focus reset (2026-08-15 ~18:35):** Google TV home **remembers** last selector position; DPAD fallback must reset focus before DOWN/RIGHT or wrong app opens (e.g. `com.tcl.tv`). **Superseded (~18:40):** `DPAD_UP`×5 + `DPAD_LEFT`×5 did not reliably reset focus. **New reset:** after package `play_media` fails, `HOME` → 300ms → `HOME` → 300ms → `DPAD_DOWN`×`app_dpad_down` → `DPAD_RIGHT`×`app_dpad_right` → `ENTER` (300ms between each press). Initial streaming path: `HOME` + 1s before `play_media`, then 2s wait before fallback. Wrapper defaults: Plex `down:2 right:1`; Jellyfin `down:2 right:2`; Stremio `down:2 right:3`.
- **Jellyfin DPAD timing (2026-08-15 ~18:45):** User saw HOME×2 but no visible DOWN/RIGHT/ENTER — old 1s/2s gaps between HOME presses and 500ms DPAD delays were too slow; TCL needs **300ms** between each press. **Fix:** all DPAD fallback delays → 300ms; package wait 4s→2s; initial HOME wait 3s→1s.
- **Jellyfin vs Plex DPAD (2026-08-15 ~18:50):** Plex DPAD worked; Jellyfin showed HOME×2 then nothing. **Root cause:** YAML blocks were identical — not structure. When helper changed **Plex → Jellyfin**, `input_select` update re-fired **Main Media - Run script from helper**, which **restarted** `script.main_media_set` (`mode: restart`) with only `media_activity` (no `app_dpad_down`). Repeat template then threw `UndefinedError: 'app_dpad_down' is undefined` after HOME×2 — no DOWN/RIGHT/ENTER. Plex test worked because helper was **already Plex** (no helper transition → no automation restart). **Fix:** sync guard on at script start / off at end; `dpad_down` / `dpad_right` variables with per-app defaults; automation passes DPAD counts; fallback `if` uses `app_id != app_pkg`. MCP retest: `script.main_media_jellyfin` → `org.jellyfin.androidtv`; `script.main_media_plex` → `com.plexapp.android`.
- **Jellyfin test (2026-08-15 ~18:45, 300ms timing):** Reloaded scripts; ran `script.main_media_jellyfin` once. MCP after ~18s: AVR **TV Audio**, HOT **off**, TCL **on**, `app_id` **com.google.android.apps.tv.launcherx** (launcher — Jellyfin **not** detected). Helper briefly **Jellyfin** then sync wrote **Plex**. **Pending user visual:** full DPAD sequence (HOME×2 + DOWN×2 + RIGHT×2 + ENTER) visible? Jellyfin launched?
- **Plex/Jellyfin confirmed (2026-08-15 ~18:55):** User confirmed Plex and Jellyfin work well with 300ms DPAD timing.
- **DPAD timing tweak (2026-08-15 ~19:00):** Reduced all DPAD fallback gaps **300ms → 200ms** (`00:00:00.200`); initial HOME wait before `play_media` **1s → 800ms** (`00:00:00.800`). Package wait stays **2s**.
- **Stremio test (2026-08-15 ~19:00, 200ms timing):** User confirmed Stremio opens reliably at 200ms.
- **DPAD timing tweak (2026-08-15 ~19:10):** Reduced all DPAD fallback gaps **100ms → 75ms** (`00:00:00.075`).
- **Stremio test (2026-08-15 ~19:10, 75ms timing):** Ran `script.main_media_stremio` **2×**. MCP: `app_id` **com.stremio.one** (2/2 pass). **Pending user visual.**
- **DPAD fallback HOME count (2026-08-15 ~19:00):** MCP A/B from launcher with wrong grid focus: **zero** fallback `HOME` → Apple TV / launcher (fail); **one** fallback `HOME` + 200ms → **com.plexapp.android** (pass); second fallback `HOME` redundant. Initial script `HOME` exits app; one fallback `HOME` resets grid focus. No native reset in `androidtv_remote` (`HOME` only; `MOVE_HOME` not in HA docs). **Fix:** fallback `HOME`×2 → `HOME`×1 in `scripts.yaml` (Plex/Jellyfin/Stremio).
- **AVR volume:** `script.main_media_youtube_michelle` sets Marantz to **35%** (`volume_level: 0.35`). No prior HOT volume-restore pattern in repo. **HOT** branch now sets AVR to **50%** (`volume_level: 0.5`) after source switch so Michelle/YouTube sessions do not leave cable at 35%.
- **HomeKit TCL TV (re-paired 2026-08-15 ~17:37):** **Working.** New config entry `01M02XPGWTRY8RX32GXQS91ED6` (title **85C855**), pairing id `85:74:DE:04:36:BF`, **AccessoryPort 35483** at `192.168.1.212` (old entry `01K4R2FJCTMXB1H7GDCBDN4YQ3` / port **35099** removed). Live entities: `media_player.85c855_television` (**on**, source **Home**), `switch.85c855_mute` (**off**), `button.85c855_identify` (**unknown** — normal for button). `source_list` includes **Cable** and **Playstation** (plus Home, AirPlay, PS5, etc.). Port **35483** accepts TCP; **35099** refused. `media_player.select_source` → **Cable** verified, then reverted to **Home**. **Entity registry cleanup (2026-08-15 ~17:44):** `_2` suffix removed via websocket API; YAML/docs reverted to canonical names. One log WARNING when old accessory was deleted without remote unpair (expected during re-pair).
- **SmartIR:** `controller_data` must be `remote.rmproplus_42_d7_58` (not IP `192.168.1.15`) — fixed in `media_player.yaml` and `climate.yaml`.
- **Google Assistant:** new script aliases need **HA restart** (`google_assistant.reload` returned 400).
- **automations.yaml:** restored truncated `ha_show_release_notes_once_after_update_install` at end of file.

See [automations-main-media.md](automations-main-media.md).

**YouTube Michelle (2026-08-15):** New standalone `script.main_media_youtube_michelle` — TV + AVR TV Audio, volume **35** (`volume_level: 0.35`), YouTube via `https://www.youtube.com`, DPAD profile pick (`profile_dpad_right`, default 1). No deep link for named Kids profile. Google Assistant **Script YouTube Michelle** — restart HA to sync GA after config change.

---

## Changelog

| Date | Change |
| ---- | ------ |
| 2026-08-15 | DPAD fallback timing: 75ms between all presses; Stremio 2/2 MCP pass. |
| 2026-08-15 | DPAD fallback timing: 200ms between all presses; package wait 2s; initial HOME wait 800ms (TCL calibration). |
| 2026-08-15 | DPAD fallback timing: 300ms between all presses; package wait 2s; initial HOME wait 1s (TCL calibration). |
| 2026-08-15 | Plex DPAD: home-grid focus reset (UP×5 LEFT×5), no ALL_APPS; wrapper down:2 right:1. |
| 2026-08-15 | Plex debug: package com.plexapp.android confirmed; URL launch fails; DPAD calibration needed; snapshot in PLEX_DEBUG_SNAPSHOT_2026-08-15.md. |
| 2026-08-15 | Netflix URL launch PASS (user TV confirm); HOT box conditional IR (no duplicate turn_off); Jellyfin DPAD test run pending visual. |
| 2026-08-15 | Main media: DPAD Apps-row launch for Plex/Jellyfin/Stremio; removed katniss search/text fallback (voice search incompatible). |
| 2026-08-15 | Main media: per-app launch (no shared URL/market chain); katniss stale-query clear; sensor Cable→HOT only when AVR ≠ TV Audio. |
| 2026-08-15 | Jellyfin launch: URL-first for Netflix/YouTube/Plex; multi-fallback chain + `app_search_name`; HOT turn_off sequential. MCP: packages fail, URLs work. |
| 2026-08-15 | Main media: sync guard + streaming→HOT block stops HOT box re-trigger; app launch via `play_media` package. |
| 2026-08-15 | Main media live-test fixes: HOME delay 4s, app verify 30s, sequential URL/`market://` fallbacks; HOT AVR volume 50%. |
| 2026-08-15 | HomeKit TCL 85C855 re-paired: new entry `01M02XPGWTRY8RX32GXQS91ED6`, HAP port **35483**, entities `*_2` available; Cable select_source OK; main_media YAML still points at old entity ids. |
| 2026-08-15 | HomeKit TCL 85C855 automated re-check: TV online, HAP/mDNS absent, port 35099 refused; reload_config_entry + identify attempted; re-pair steps unchanged. |
| 2026-08-15 | `script.main_media_youtube_michelle`: AVR vol 35, YouTube Kids profile Michelle (DPAD best-effort); GA exposure. |
| 2026-08-15 | Main media: SmartIR remote entity fix; app URL launches; HomeKit HAP down on TCL (TV settings); HDMI remote fallbacks; HA restart for Google Assistant. |
| 2026-08-15 | Main media switcher + best-guess sensor; AVR TV Audio except HOT; PS = TV HDMI 1; no Unknown; loop break. |
| 2026-08-07 | Cleared stale Telegram repair `migrate_chat_ids_in_target_call_service_send_message` (origin `call_service`, not YAML). No `telegram_bot.send_message`+`target` left in config; automations already use notify entity. |
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
