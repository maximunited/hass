#!/command/with-contenv bash
# ==============================================================================
# S6-overlay script to install custom python packages from HACS requirements
# ==============================================================================

echo ">>> Installing pip requirements for custom HACS packages..."

find /config/custom_components -name "manifest.json" -print0 \
    | xargs -0 jq -r "(.requirements // [])[]" \
    | xargs -r pip install

echo ">>> Finished custom HACS packages installation."
