"""Sensor component."""

from __future__ import annotations

import asyncio

from .logger import _LOGGER
from enum import Enum
from typing import Any, Final

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfInformation, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_SENSOR_AP_SIGNAL,
    ATTR_SENSOR_AP_SIGNAL_NAME,
    ATTR_SENSOR_DEVICES,
    ATTR_SENSOR_DEVICES_2_4,
    ATTR_SENSOR_DEVICES_2_4_NAME,
    ATTR_SENSOR_DEVICES_5_0,
    ATTR_SENSOR_DEVICES_5_0_GAME,
    ATTR_SENSOR_DEVICES_5_0_GAME_NAME,
    ATTR_SENSOR_DEVICES_5_0_NAME,
    ATTR_SENSOR_DEVICES_GUEST,
    ATTR_SENSOR_DEVICES_GUEST_NAME,
    ATTR_SENSOR_DEVICES_LAN,
    ATTR_SENSOR_DEVICES_LAN_NAME,
    ATTR_SENSOR_DEVICES_NAME,
    ATTR_SENSOR_MEMORY_TOTAL,
    ATTR_SENSOR_MEMORY_TOTAL_NAME,
    ATTR_SENSOR_MEMORY_USAGE,
    ATTR_SENSOR_MEMORY_USAGE_NAME,
    ATTR_SENSOR_MODE,
    ATTR_SENSOR_MODE_NAME,
    ATTR_SENSOR_TEMPERATURE,
    ATTR_SENSOR_TEMPERATURE_NAME,
    ATTR_SENSOR_UPTIME,
    ATTR_SENSOR_UPTIME_NAME,
    ATTR_SENSOR_VPN_UPTIME,
    ATTR_SENSOR_VPN_UPTIME_NAME,
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED_NAME,
    ATTR_SENSOR_WAN_UPLOAD_SPEED,
    ATTR_SENSOR_WAN_UPLOAD_SPEED_NAME,
    ATTR_SENSOR_WAN_IP,
    ATTR_SENSOR_WAN_IP_NAME,
    ATTR_SENSOR_WAN_TYPE,
    ATTR_SENSOR_WAN_TYPE_NAME,
    ATTR_STATE,
)
from .entity import MiWifiEntity
from .enum import DeviceClass
from .updater import LuciUpdater, async_get_updater

PARALLEL_UPDATES = 0

DISABLE_ZERO: Final = (
    ATTR_SENSOR_TEMPERATURE,
    ATTR_SENSOR_AP_SIGNAL,
)

ONLY_WAN: Final = (
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
    ATTR_SENSOR_WAN_UPLOAD_SPEED,
)

PCS: Final = "pcs"
BS: Final = "B/s"
MBPS: Final = "Mb/s"

MIWIFI_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_SENSOR_UPTIME,
        name=ATTR_SENSOR_UPTIME_NAME,
        icon="mdi:timer-sand",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_VPN_UPTIME,
        name=ATTR_SENSOR_VPN_UPTIME_NAME,
        icon="mdi:timer-sand",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MEMORY_USAGE,
        name=ATTR_SENSOR_MEMORY_USAGE_NAME,
        icon="mdi:memory",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MEMORY_TOTAL,
        name=ATTR_SENSOR_MEMORY_TOTAL_NAME,
        icon="mdi:memory",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_TEMPERATURE,
        name=ATTR_SENSOR_TEMPERATURE_NAME,
        icon="mdi:temperature-celsius",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MODE,
        name=ATTR_SENSOR_MODE_NAME,
        icon="mdi:transit-connection-variant",
        device_class=DeviceClass.MODE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_AP_SIGNAL,
        name=ATTR_SENSOR_AP_SIGNAL_NAME,
        icon="mdi:wifi-arrow-left-right",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
        name=ATTR_SENSOR_WAN_DOWNLOAD_SPEED_NAME,
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_UPLOAD_SPEED,
        name=ATTR_SENSOR_WAN_UPLOAD_SPEED_NAME,
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES,
        name=ATTR_SENSOR_DEVICES_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_LAN,
        name=ATTR_SENSOR_DEVICES_LAN_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_2_4,
        name=ATTR_SENSOR_DEVICES_2_4_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_5_0,
        name=ATTR_SENSOR_DEVICES_5_0_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_GUEST,
        name=ATTR_SENSOR_DEVICES_GUEST_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_5_0_GAME,
        name=ATTR_SENSOR_DEVICES_5_0_GAME_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_IP,
        name=ATTR_SENSOR_WAN_IP_NAME,
        icon="mdi:ip",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_TYPE,
        name=ATTR_SENSOR_WAN_TYPE_NAME,
        icon="mdi:lan",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
)




async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MiWiFi sensors without blocking startup."""
    hass.async_create_task(
        _async_add_all_sensors_later(hass, config_entry, async_add_entities)
    )



from .const import (
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
    ATTR_SENSOR_WAN_UPLOAD_SPEED,
    CONF_WAN_SPEED_UNIT,
    DEFAULT_WAN_SPEED_UNIT,
)

class MiWifiSensor(MiWifiEntity, SensorEntity):
    """MiWifi sensor entity."""

    def __init__(
        self,
        unique_id: str,
        description: SensorEntityDescription,
        updater: LuciUpdater,
    ) -> None:
        super().__init__(unique_id, description, updater, ENTITY_ID_FORMAT)
        self._attr_native_value = self._compute_value()
        self._attr_native_unit_of_measurement = self._compute_unit()

    def _handle_coordinator_update(self) -> None:
        """Update state from coordinator."""
        is_available: bool = self._updater.data.get(ATTR_STATE, False)

        new_value = self._compute_value()
        new_unit = self._compute_unit()

        if (
            self._attr_native_value == new_value
            and self._attr_native_unit_of_measurement == new_unit
            and self._attr_available == is_available  # type: ignore
        ):
            return

        self._attr_available = is_available
        self._attr_native_value = new_value
        self._attr_native_unit_of_measurement = new_unit
        self.async_write_ha_state()

    def _compute_value(self):
        """Compute sensor value with conversion if needed."""
        value = self._updater.data.get(self.entity_description.key)

        if self.entity_description.key in (
            ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
            ATTR_SENSOR_WAN_UPLOAD_SPEED,
        ):
            unit = (
                self._updater.config_entry.options.get(CONF_WAN_SPEED_UNIT, DEFAULT_WAN_SPEED_UNIT)
                if self._updater.config_entry
                else DEFAULT_WAN_SPEED_UNIT
            )
            if unit == "Mbps" and isinstance(value, (int, float)):
                return round(value / 1024 / 1024, 2)

        if isinstance(value, Enum):
            return value.phrase

        return value

    def _compute_unit(self):
        """Determine unit based on user setting."""
        if self.entity_description.key in (
            ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
            ATTR_SENSOR_WAN_UPLOAD_SPEED,
        ):
            unit = (
                self._updater.config_entry.options.get(CONF_WAN_SPEED_UNIT, DEFAULT_WAN_SPEED_UNIT)
                if self._updater.config_entry
                else DEFAULT_WAN_SPEED_UNIT
            )
            return "Mb/s" if unit == "Mbps" else "B/s"

        return self.entity_description.native_unit_of_measurement
    
class MiWifiTopologyGraphSensor(SensorEntity):
    """Sensor to represent the network topology graph."""

    def __init__(self, updater: LuciUpdater) -> None:
        self._attr_unique_id = f"{updater.entry_id}_topology_graph"
        self._attr_name = "Topología MiWiFi"
        self._updater = updater
        self._attr_icon = "mdi:network"
        self._attr_should_poll = False

    @property
    def native_value(self) -> str:
        """Return the state of the topology sensor."""
        return "ok" if self._updater.data.get("topo_graph") else "unavailable"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the topology graph as attributes."""
        return self._updater.data.get("topo_graph", {})


    async def async_update(self) -> None:
        """No polling, data is pushed from coordinator."""
        pass

from homeassistant.helpers.entity import Entity
from .const import CONF_ENABLE_PANEL, CONF_WAN_SPEED_UNIT, CONF_LOG_LEVEL
from .helper import get_global_log_level
from .logger import _LOGGER
from datetime import datetime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class MiWifiConfigSensor(CoordinatorEntity, SensorEntity):
    """Sensor que expone la configuración actual como atributos."""

    def __init__(self, updater: LuciUpdater) -> None:
        super().__init__(updater)
        self._updater = updater
        self._attr_name = "MiWiFi Config"
        self._attr_unique_id = f"{updater.entry_id}_config"
        self._attr_icon = "mdi:cog"
        self._attr_should_poll = False
        self._attr_native_value = "ok"
        self._extra_attrs: dict[str, Any] = {}

    @property
    def state(self) -> str:
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._extra_attrs

    async def async_added_to_hass(self) -> None:
        """Se ejecuta al agregar la entidad a Home Assistant."""
        await super().async_added_to_hass()
        await self._update_attrs()
        self._unsub_coordinator_update = self._updater.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self) -> None:
        self.hass.async_create_task(self._update_attrs())

    async def _update_attrs(self) -> None:
        from .helper import get_global_log_level
        from .frontend import read_local_version

        log_level = await get_global_log_level(self._updater.hass)
        panel_version = await read_local_version(self._updater.hass)
        config = self._updater.config_entry.options

        self._extra_attrs = {
            "panel_activo": config.get("enable_panel", True),
            "speed_unit": config.get("wan_speed_unit", "MB"),
            "log_level": log_level,
            "panel_version": panel_version,
            "last_checked": datetime.now().isoformat(),
        }

        self.async_write_ha_state()


async def _async_add_all_sensors_later(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add all MiWiFi sensors asynchronously to avoid blocking startup."""

    await asyncio.sleep(0)

    updater: LuciUpdater = async_get_updater(hass, config_entry.entry_id)

    entities: list[SensorEntity] = [
        MiWifiTopologyGraphSensor(updater),
        MiWifiConfigSensor(updater),
    ]

    for description in MIWIFI_SENSORS:
        if description.key == ATTR_SENSOR_DEVICES_5_0_GAME and not updater.supports_game:
            continue

        if description.key in DISABLE_ZERO and updater.data.get(description.key, 0) == 0:
            continue

        if description.key in ONLY_WAN and not updater.supports_wan:
            continue

        entities.append(
            MiWifiSensor(
                f"{config_entry.entry_id}-{description.key}",
                description,
                updater,
            )
        )

    async_add_entities(entities)
