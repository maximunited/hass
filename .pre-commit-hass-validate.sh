#!/bin/bash
# Home Assistant configuration validation script for pre-commit

if command -v hass >/dev/null 2>&1; then
    hass --script check_config --config . || exit 1
else
    echo "Warning: hass command not found. Install Home Assistant to validate config."
    exit 0
fi