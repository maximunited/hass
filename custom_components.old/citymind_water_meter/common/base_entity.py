import logging
import sys
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from ..managers.coordinator import Coordinator
from .consts import ADD_COMPONENT_SIGNALS, DOMAIN
from .entity_descriptions import IntegrationEntityDescription, get_entity_descriptions
from .enums import EntityType

_LOGGER = logging.getLogger(__name__)


async def async_setup_base_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    platform: Platform,
    entity_type_ctor: type,
    async_add_entities,
):
    @callback
    def _async_handle_device(
        entry_id: str, entity_type: EntityType, meter_id: str | None = None
    ):
        if entry.entry_id != entry_id:
            return

        try:
            coordinator = hass.data[DOMAIN][entry.entry_id]

            entity_descriptions = get_entity_descriptions(platform, entity_type)

            entities = [
                entity_type_ctor(
                    hass, entity_description, coordinator, entity_type, meter_id
                )
                for entity_description in entity_descriptions
            ]

            async_add_entities(entities, True)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to initialize {platform}, Error: {ex}, Line: {line_number}"
            )

    for add_component_signal in ADD_COMPONENT_SIGNALS:
        entry.async_on_unload(
            async_dispatcher_connect(hass, add_component_signal, _async_handle_device)
        )


class IntegrationBaseEntity(CoordinatorEntity):
    _entity_description: IntegrationEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entity_description: IntegrationEntityDescription,
        coordinator: Coordinator,
        entity_type: EntityType,
        meter_id: str | None,
    ):
        super().__init__(coordinator)

        try:
            self.hass = hass
            self._meter_id = meter_id
            self._entity_type = entity_type

            device_info = coordinator.get_device_info(entity_description, meter_id)

            entity_name = coordinator.config_manager.get_entity_name(
                entity_description, device_info
            )

            unique_id_parts = [
                DOMAIN,
                entity_description.platform,
                entity_description.key,
                meter_id,
            ]

            unique_id_parts_clean = [
                unique_id_part
                for unique_id_part in unique_id_parts
                if unique_id_part is not None
            ]

            unique_id = slugify("_".join(unique_id_parts_clean))

            self.entity_description = entity_description
            self._entity_description = entity_description

            self._attr_device_info = device_info
            self._attr_name = entity_name
            self._attr_unique_id = unique_id

            self._data = {}

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to initialize {entity_description}, Error: {ex}, Line: {line_number}"
            )

    @property
    def _local_coordinator(self) -> Coordinator:
        return self.coordinator

    @property
    def data(self) -> dict | None:
        return self._data

    async def async_execute_device_action(self, key: str, *kwargs: Any):
        async_device_action = self._local_coordinator.get_device_action(
            self._entity_description, self._meter_id, key
        )

        if self._entity_description.entity_type == EntityType.ACCOUNT:
            await async_device_action(self._entity_description, *kwargs)

        else:
            await async_device_action(self._entity_description, self._meter_id, *kwargs)

        await self.coordinator.async_request_refresh()

    def update_component(self, data):
        pass

    def _handle_coordinator_update(self) -> None:
        """Fetch new state parameters for the sensor."""
        try:
            new_data = self._local_coordinator.get_data(
                self._entity_description, self._meter_id
            )

            if self._data != new_data:
                self.update_component(new_data)

                self._data = new_data

                self.async_write_ha_state()

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to update {self.unique_id}, Error: {ex}, Line: {line_number}"
            )
