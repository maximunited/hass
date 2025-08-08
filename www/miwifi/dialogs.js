import { localize } from "./translations/localize.js?v=1.3.9";
import { logToBackend } from "./pages/utils.js?v=1.3.9";

/**
 * Get current main router MAC from sensor
 */
function getCurrentMainMac() {
  const hass = document.querySelector("home-assistant")?.hass;
  const sensors = Object.values(hass?.states || {}).filter(
    (s) =>
      s.entity_id.startsWith("sensor.miwifi_topology") &&
      s.attributes?.graph?.is_main === true
  );
  return sensors.length ? sensors[0].attributes.graph.mac : null;
}

/**
 * Show selection dialog for choosing the main router
 */
export async function showDialog(hass, { title, options, onSelect }) {
  const content = document.createElement("div");
  content.style.padding = "16px";

  if (!options?.length) {
    await logToBackend(hass, "warning", "❌ No router candidates found for manual selection (dialogs.js)");
    return;
  }

  const currentMain = getCurrentMainMac();

  options.forEach((opt) => {
    const isSelected = currentMain === opt.mac;
    const btn = document.createElement("mwc-button");

    btn.innerText = isSelected
      ? `✅ ${opt.name} (${localize("button_selected")})`
      : opt.name;

    btn.style.margin = "4px";

    btn.addEventListener("click", async () => {
      const isDeselect = isSelected;
      const selectedMac = isDeselect ? "" : opt.mac;

      try {
        await hass.callService("miwifi", "select_main_router", { mac: selectedMac });

        await hass.callService("miwifi", "log_panel", {
          level: "info",
          message: `🖱️ User selected router: ${selectedMac || "none (cleared)"}`,
        });

        await logToBackend(hass, "info", `🖱️ Manual router ${selectedMac || "cleared"} selected from UI (dialogs.js)`);

      } catch (err) {
        console.error("🛑 Error al llamar al servicio select_main_router:", err);
        await logToBackend(hass, "error", `❌ Failed to call select_main_router: ${err}`);
      }

      dialog.close();
      location.reload();
    });

    content.appendChild(btn);
  });

  const dialog = document.createElement("ha-dialog");
  dialog.heading = title;
  dialog.appendChild(content);
  document.body.appendChild(dialog);

  await customElements.whenDefined("ha-dialog");
  await new Promise((r) => setTimeout(r, 50));

  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
}
