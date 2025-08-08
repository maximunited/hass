import { html } from "https://unpkg.com/lit@2.7.5/index.js?module";
import { localize } from "../translations/localize.js?v=1.3.9";

export function renderError(hass) {
  return html`
    <div class="content text-center">
      <h2>${localize("error_title")}</h2>
      <p>${localize("error_not_found")}</p>
      <p>${localize("error_suggestion")}</p>
    </div>
  `;
}
