#!/bin/bash
# Ping Healthchecks.io for the RPi check monitored by binary_sensor.rpi_heartbeat.
# Install on the Pi: see repo-docs/HA_DIAGNOSTICS.md (RPi heartbeat section).
set -euo pipefail
URL="${HEALTHCHECKS_RPI_URL:-https://hc-ping.com/your-rpi-check-uuid-here}"
curl -fsS -m 10 --retry 3 "${URL}" || true
