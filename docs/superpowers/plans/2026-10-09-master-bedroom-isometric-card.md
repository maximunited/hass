# Master Bedroom isometric animated card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put a tikel1-style animated picture-elements card on Master Bedroom wired to North/West Shelly blinds and the Lenovo smart clock.

**Architecture:** Decluttered still → isometric background → Kling blinds videos → ffmpeg WebM/PNG → `ha-blinds-frame-card` overlays on Lovelace view 5.

**Tech Stack:** Home Assistant Lovelace (storage), Kling CLI/API, ffmpeg, Cursor image gen, `ha-blinds-frame-card.js`.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-10-09-master-bedroom-isometric-card-design.md`
- Kling token via env only; never commit
- North blinds = shutter above headboard: `cover.shellyplus2pm_2cbcbb3f3978`
- West blinds = behind grey curtains: `cover.m_bedroom_west_blinds`
- Clock on right nightstand: `media_player.master_bedroom_clock`
- Ceiling unit: retractable fan+light+BT (Payngo 290799 look). Idle = blades folded. Light badge → `light.shellyplus1_7c87ce72af20_m_bedroom_main_light`. No `fan.*` in HA — skip spin loop unless user adds control later
- Assets under `www/images/master-bedroom/`
- Do not mass-edit `custom_components/` / `www/community/`

---

## File map

| Path | Role |
| ---- | ---- |
| `www/images/master-bedroom/master-bedroom-clean.jpg` | Approved decluttered still |
| `www/images/master-bedroom/background.jpg` | Isometric card background |
| `www/images/master-bedroom/north_blinds_*` | North shutter animation |
| `www/images/master-bedroom/west_blinds_*` | West blinds animation |
| `www/ha-blinds-frame-card.js` | Custom card module |
| Lovelace resources + `lovelace` view 5 | Resource + picture-elements card |

---

### Task 1: Finalize clean still (clock on right nightstand)

- [x] Clean still iterated; geometry (equal windows / tall NS / fan scale) deferred to isometric prompt (user chose path B)
- [x] Copy to `www/images/master-bedroom/master-bedroom-clean.jpg`

### Task 2: Isometric background

- [x] Isometric saved as `www/images/master-bedroom/background.jpg` (geometry imperfect; user proceeded)

### Task 3: Install Kling CLI + ffmpeg

- [x] `ffmpeg` static in `~/.local/bin`; `kling-pro-cli` via pipx
- [x] Official Kling API key tried → **code 1102 Account balance not enough**; AceDataCloud token invalid for this key

### Task 4–5: Animations (fallback)

- [x] Open→closed stills + ffmpeg blend → `north_blinds_100f.webm` / `west_blinds_100f.webm` + PNG sequences (replace with Kling when credited)

### Task 6: Install custom card + resource

- [x] `www/ha-blinds-frame-card.js` (+ fan card); Lovelace resources registered

### Task 7: Picture-elements on Master Bedroom

- [x] Live config saved via HA websocket; card on views[5]

```yaml
type: picture-elements
image: /local/images/master-bedroom/background.jpg
elements:
  - type: custom:ha-blinds-frame-card
    entity: cover.shellyplus2pm_2cbcbb3f3978
    src: /local/images/master-bedroom/north_blinds_100f.webm
    png_path: /local/images/master-bedroom/north_blinds_
    frames: 100
    fps: 25
    speed: 0.5
    style:
      left: 55%
      top: 28%
      width: 22%
      height: 28%
  - type: custom:ha-blinds-frame-card
    entity: cover.m_bedroom_west_blinds
    src: /local/images/master-bedroom/west_blinds_100f.webm
    png_path: /local/images/master-bedroom/west_blinds_
    frames: 100
    fps: 25
    speed: 0.5
    style:
      left: 22%
      top: 35%
      width: 18%
      height: 40%
  - type: state-badge
    entity: media_player.master_bedroom_clock
    style:
      left: 68%
      top: 58%
  - type: state-icon
    entity: light.shellyplus1_7c87ce72af20_m_bedroom_main_light
    style:
      left: 50%
      top: 12%
```

- [ ] Tune `%` after visual check on `https://hass.malter.duckdns.org/lovelace/5`
- [ ] Keep existing media / blinds / thermostat cards

**Verify:** MCP `get_dashboard_config`; browser/HA shows card; moving covers animates overlays; clock badge present.

### Task 8: Docs touch-up

- [ ] Note live card + asset paths in `repo-docs/HA_DIAGNOSTICS.md` only if operationally useful (short pointer)
- [ ] Run markdownlint on touched `.md` if edited

**Verify:** Lint clean on edited md files.
