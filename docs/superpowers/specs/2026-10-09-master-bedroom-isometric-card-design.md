# Master Bedroom isometric animated picture card

## Goal

Add a tikel1-style animated `picture-elements` card to the Master Bedroom Lovelace view (`lovelace` dashboard, view index 5), driven by real cover entities, with AI-generated isometric room art and Kling blinds animations.

## Source imagery

- **Primary:** newer furnished bedroom photo (curtains, AC, ceiling fan, hexagonal mirror) provided in-session.
- **Secondary reference:** `2017-11-09 18.05.44.jpg` / bed-facing window shot for north window + shutter geometry.
- **Declutter before isometric:** remove bassinet, nursing pillow, pet bed, chair, clothes on headboard, nightstand clutter, trash; left nightstand empty; right nightstand has Lenovo Smart Clock; solid neutral bedding (not horse print).
- **Nightstands:** floating wall-mounted white single-drawer units (no legs), attached to the back wall with visible gap above the floor; ~70% larger than first drafts; switch/outlet plates directly above each.
- **Layout:** bed/window/nightstand group offset right; clear chair-width gap left of left nightstand (no chair in render). Grey-tone hardwood. AC in opposite corner from both windows — out of frame in this camera angle.
- **Clock:** Lenovo Smart Clock Essential (grey fabric wedge, LED time face) on right nightstand.
- **Ceiling fixture:** retractable-blade white fan + drum light (+ BT music) above the bed — product ref [Payngo 290799](https://www.payngo.co.il/290799.html). Blades fan out when spinning, fold in when idle. No dedicated `fan.*` entity in HA today.

## Architecture

| Piece | Choice |
| ----- | ------ |
| Background | Decluttered → 1:1 isometric cutaway still (`www/images/master-bedroom/background.jpg`) |
| Animations | Kling image-to-video, camera locked; North shutter + West blinds/curtains |
| Cards | `ha-blinds-frame-card` (WebM + PNG sequence fallback) |
| Fan | Correct product look in stills (folded idle). Loop animation only if a controllable entity exists; otherwise visual + optional light/BT badge |
| Dashboard | Prepend picture-elements on Master Bedroom; keep media / blinds sliders / AC |

## Entities

| Overlay | Entity | Notes |
| ------- | ------ | ----- |
| North blinds | `cover.shellyplus2pm_2cbcbb3f3978` | Rolling shutter above headboard window |
| West blinds | `cover.m_bedroom_west_blinds` | Behind the grey curtains (left wall) |
| Lenovo smart clock | `media_player.master_bedroom_clock` | On the **right** nightstand; state badge / tap (`device_tracker.lenovo_smart_clock` related) |
| Optional badges | `light.shellyplus1_7c87ce72af20_m_bedroom_main_light`, `light.m_bedroom_hall_light`, door / AC | |

## File layout

```text
www/
  ha-blinds-frame-card.js
  images/master-bedroom/
    background.jpg
    north_blinds_100f.webm
    north_blinds_XXX.png
    west_blinds_100f.webm
    west_blinds_XXX.png
```

## Pipeline

1. Generate decluttered clean still; **user approves**.
2. Generate isometric cutaway from clean still; user may tweak.
3. Kling: north shutter open→closed; west blinds open→closed (stationary camera).
4. ffmpeg: extract PNG frames, encode seekable WebM (`yuva420p` where possible).
5. Install card JS + Lovelace resource; place picture-elements on view 5; tune overlay `%` positions.

## Secrets

- Kling API token via environment only (e.g. `ACEDATACLOUD_API_TOKEN` / `KLING_API_KEY`).
- Never commit the token to the repo or this spec.

## Out of scope (v1)

- Fan spin loop until a real `fan.*` / IR / BT entity is available to drive `ha-fan-loop-card`
- Day/night lighting animation
- Replacing existing Master Bedroom entities cards
