import { LitElement, html, css } from "https://unpkg.com/lit@2.7.5/index.js?module";
import { localize } from "../translations/localize.js?v=1.3.9";

class MiWiFiNodeDeviceCard extends LitElement {
  static properties = {
    hass: {},
    devices: { type: Array },
  };

  render() {
    const connected = this.devices?.filter((d) => d.state === "home") ?? [];
    const disconnected = this.devices?.filter((d) => d.state !== "home") ?? [];

    if (!connected.length && !disconnected.length) return html``;

    const grouped = {};
    connected.forEach((device) => {
      const conn = this._getConnectionLabel(device.attributes.connection);
      if (!grouped[conn]) grouped[conn] = [];
      grouped[conn].push(device);
    });

    return html`
      <div class="section">
        <h3>📶 ${localize("devices_connected_title")}</h3>

        ${Object.entries(grouped).map(([type, devs]) => html`
          <div class="section-title">${localize("section_" + type) || type}</div>
          <div class="device-grid">
            ${devs.map((d) => this._renderCard(d))}
          </div>
        `)}

        ${disconnected.length > 0 ? html`
          <div class="section-title" style="margin-top: 32px;">
            🔴 ${localize("toggle_offline_show")}
          </div>
          <div class="device-grid">
            ${disconnected.map((d) => this._renderCard(d))}
          </div>
        ` : ""}
      </div>
    `;
  }

  _getConnectionLabel(connection) {
    switch ((connection || "").toLowerCase()) {
      case "lan": return "LAN";
      case "2.4g": return "2.4G";
      case "5g": return "5G";
      case "5g game": return "5G Game";
      case "guest": return "Guest";
      default: return "Unknown";
    }
  }

  _translateSignalQuality(quality) {
    switch (quality) {
      case "very_strong": return localize("signal_quality_very_strong");
      case "strong": return localize("signal_quality_strong");
      case "fair": return localize("signal_quality_fair");
      case "weak": return localize("signal_quality_weak");
      case "very_weak": return localize("signal_quality_very_weak");
      default: return localize("signal_quality_unknown");
    }
  }

  _renderCard(device) {
    const a = device.attributes;
    const isOffline = device.state !== "home";

    if (isOffline) {
      return html`
        <div class="device-card disconnected">
          <div class="device-name">${a.friendly_name || device.entity_id}</div>
          <div class="device-info">${localize("ip")}: ${a.ip || "-"}</div>
          <div class="device-status offline">${localize("status_disconnected")}</div>
          <div class="device-info">
            ${localize("wan_access")}: 
            ${a.internet_blocked 
              ? html`<span style="color:red;">${localize("wan_blocked")}</span>` 
              : html`<span style="color:lightgreen;">${localize("wan_allowed")}</span>`}
          </div>
          <div class="device-info-wan">
            <span>${localize("wan_unblock_button")}</span>
            <ha-switch
              .checked=${a.internet_blocked}
              @change=${(ev) => this._toggleWAN(device, ev.target.checked)}
            ></ha-switch>
            <span>${localize("wan_block_button")}</span>
          </div>
        </div>
      `;
    }

    return html`
      <div class="device-card">
        <div class="device-name">${a.friendly_name || device.entity_id}</div>
        <div class="device-info">${localize("ip")}: ${a.ip || "-"}</div>
        <div class="device-info">${localize("mac_address")}: ${a.mac || "-"}</div>
        <div class="device-info">
          <span style="color: lightgreen;">🟢</span> ${localize("status_connected")}: ${localize("status_connected_yes")}
        </div>
        ${a.connection?.toLowerCase() !== "lan" ? html`
            <div class="device-info">${localize("signal")}: ${a.signal ?? "N/D"}</div>
            <div class="device-info">${localize("signal_quality")}: ${this._translateSignalQuality(a.signal_quality)}</div>
          ` : ""}
        <div class="device-info">↑ ${a.up_speed ?? "0 B/s"}</div>
        <div class="device-info">↓ ${a.down_speed ?? "0 B/s"}</div>
        <div class="device-info">${localize("last_activity")}: ${a.last_activity ?? "-"}</div>

        <div class="device-info">
          ${localize("wan_access")}: 
          ${a.internet_blocked 
            ? html`<span style="color:red;">${localize("wan_blocked")}</span>` 
            : html`<span style="color:lightgreen;">${localize("wan_allowed")}</span>`}
        </div>

        <div class="device-info-wan">
          <span>${localize("wan_unblock_button")}</span>
          <ha-switch
            .checked=${a.internet_blocked}
            @change=${(ev) => this._toggleWAN(device, ev.target.checked)}
          ></ha-switch>
          <span>${localize("wan_block_button")}</span>
        </div>

        <div class="device-status online">${localize("status_connected")}</div>
      </div>
    `;
  }

  _toggleWAN(device, checked) {
    const entityId = device.entity_id;
    const deviceEntry = this.hass.entities[entityId]?.device_id || device.device_id;
  
    const allow = checked;
  
    this.hass.callService("miwifi", "block_device", {
      device_id: deviceEntry,
      allow: allow
    });
  }

  
  static styles = css`
    .section-title {
      font-size: 20px;
      font-weight: bold;
      color: white;
      margin-top: 24px;
      text-align: center;
    }

    .device-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      padding: 16px;
    }

    .device-card {
      background: #1a73e8;
      color: white;
      padding: 16px;
      border-radius: 12px;
      text-align: center;
      box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
      animation: fadeIn 0.5s ease;
    }

    .device-name {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 8px;
    }

    .device-info {
      font-size: 14px;
      margin-bottom: 4px;
    }

    .device-info-wan {
      font-size: 14px;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 10px;
      align-content: center;
      justify-content: center;
    }

    .device-card.disconnected {
      background-color: rgba(255, 255, 255, 0.1);
      color: #bbb;
      filter: grayscale(100%);
    }

    .device-status.offline {
      color: #ff4d4d;
      font-weight: bold;
    }

    .device-status.online {
      color: #00ff00;
      font-weight: bold;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `;
}

customElements.define("miwifi-device-node-card", MiWiFiNodeDeviceCard);
