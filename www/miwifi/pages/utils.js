import { html } from "https://unpkg.com/lit@2.7.5/index.js?module";
import { localize } from "../translations/localize.js?v=1.3.9";

export function renderToggle(hass, entity) {
  return html`
    <div class="setting-row">
      <span>${entity.attributes.friendly_name}</span>
      <label class="switch">
        <input type="checkbox"
          .checked=${entity.state === "on"}
          @change=${(e) =>
            hass.callService(entity.entity_id.split(".")[0],
              e.target.checked ? "turn_on" : "turn_off",
              { entity_id: entity.entity_id })} />
        <span class="slider"></span>
      </label>
    </div>
  `;
}

export function renderSelects(hass, selects) {
  const unique = {};
  selects.forEach(s => {
    if (!unique[s.attributes.friendly_name]) {
      unique[s.attributes.friendly_name] = s;
    }
  });

  return html`
    <div class="select-grid">
      ${Object.values(unique).map(entity => html`
        <div class="select-block">
          <label>${entity.attributes.friendly_name}</label>
          <select
            .value=${entity.state}
            @change=${(e) =>
              hass.callService("select", "select_option", {
                entity_id: entity.entity_id,
                option: e.target.value,
              })}
          >
            ${entity.attributes.options.map(opt => html`
              <option value="${opt}" ?selected=${opt === entity.state}>${opt}</option>`)}
          </select>
        </div>
      `)}
    </div>
  `;
}

export function getMainRouterMac(hass) {
  const mainGraph = Object.values(hass.states)
    .find((s) =>
      s.entity_id.startsWith("sensor.miwifi_topology") &&
      s.attributes?.graph?.is_main === true
    )?.attributes?.graph;

  return mainGraph?.mac?.toLowerCase()?.replaceAll(":", "_") ?? null;
}

export function formatSignal(value) {
  const map = {
    max: "100%",
    mid: "50%",
    min: "25%",
    unavailable: "N/D",
  };
  return map[value?.toLowerCase()] ?? value + "%";
}

export function logToBackend(hass, level, message) {
  if (!hass || !hass.callService) {
    console.warn("⚠️ [logToBackend] Home Assistant instance not ready.");
    return;
  }

  hass.callService("miwifi", "log_panel", {
    level,
    message,
  }).catch((err) => {
    console.warn("🛑 [logToBackend] Error sending log to backend:", err);
  });
}
