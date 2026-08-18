# Plex debug snapshot — 2026-08-15 ~18:28 UTC+3

User manually switched TV to Plex. MCP capture + HOME + restore attempts.

## Step 1 — ON PLEX (baseline)

| Entity | State | Key attributes |
| ------ | ----- | -------------- |
| `media_player.tcl_tv` | on | `app_id`: **com.plexapp.android**, `app_name`: com.plexapp.android |
| `remote.tcl_tv` | on | `current_activity`: **com.plexapp.android**, `activity_list`: [] |
| `media_player.marantz_nr1608` | on | `source`: **TV Audio**, `volume_level`: 0.515, `sound_mode`: VIRTUAL |
| `media_player.85c855_television` | on | `source`: **Home** |
| `media_player.living_room_hot` | off | (no source) |
| `input_select.main_media` | **Plex** | |
| `sensor.main_media_detected` | **Plex** | |
| `media_player.tcl_tv_2` | unavailable | restored ghost |

### Plex-related entities (search "plex")

| Entity | State | Note |
| ------ | ----- | ---- |
| `script.main_media_plex` | off | |
| `sensor.plex_hassvm` | 0 watching | |
| `sensor.docker_plex_state` | running | |
| `sensor.docker_plex_health` | healthy | |
| `media_player.plex_plex_for_android_tv_smart_tv_pro` | unavailable | Plex integration client |
| `media_player.smart_tv_pro` | idle | Cast/DLNA duplicate |

## Step 2 — AFTER HOME (3s wait)

| Entity | State | Key attributes |
| ------ | ----- | -------------- |
| `media_player.tcl_tv` | on | `app_id`: **com.google.android.apps.tv.launcherx** |
| `remote.tcl_tv` | on | `current_activity`: **com.google.android.apps.tv.launcherx** |
| `input_select.main_media` | Plex | unchanged (manual) |
| `sensor.main_media_detected` | Plex | stale — template keeps `prev` on launcher |

HOME command: **success** (launcher confirmed).

## Step 3 — Restore attempts

| # | Method | Service call | Result (HA entity) |
| - | ------ | ------------ | ------------------ |
| 1 | Package `play_media` | `media_player.play_media` app `com.plexapp.android` | **FAIL** — still launcher |
| 2 | Activity `remote.turn_on` | activity `com.plexapp.android` | **FAIL** — still launcher |
| 3 | URL `play_media` | `https://app.plex.tv` | **FAIL** — still launcher |
| 4 | URL `remote.turn_on` | activity `https://app.plex.tv` | **FAIL** — still launcher |
| 5 | Full script | `script.main_media_plex` (default DPAD down:1 right:0) | **FAIL** — still launcher after ~22s |
| 6 | Manual DPAD | ALL_APPS → DOWN×2 → ENTER | **WRONG APP** — `com.tcl.tv` (HDMI input) |

## Step 4 — Final state (after manual DPAD)

| Entity | State | Key attributes |
| ------ | ----- | -------------- |
| `media_player.tcl_tv` | on | `app_id`: **com.tcl.tv** |
| `remote.tcl_tv` | on | `current_activity`: **com.tcl.tv** |
| `media_player.marantz_nr1608` | on | `source`: TV Audio, vol 0.515 |
| `media_player.living_room_hot` | off | unchanged ✓ |
| `sensor.main_media_detected` | Plex | stale (prev kept) |

## Conclusions

1. **Plex package when running:** `com.plexapp.android` — matches `script.main_media_set` variable.
2. **Package `play_media`:** silent fail (same as Jellyfin; documented 2026-08-15).
3. **Plex URL:** does **not** launch app (unlike Netflix `https://www.netflix.com/title` and YouTube `https://www.youtube.com`).
4. **Restore:** none of the automated methods restored Plex per HA `app_id`. DPAD fallback needs **tile calibration** (`app_dpad_down` / `app_dpad_right`).
5. **HOT box:** stayed **off** throughout ✓
6. **Detection gap:** `sensor.main_media_detected` kept **Plex** while TV was on launcher / `com.tcl.tv` (template `prev` fallback).

## Calibration next step

Developer Tools → Services → `script.main_media_plex` → tune `app_dpad_down` / `app_dpad_right` on Apps row (same as Jellyfin). User visual confirm required.
