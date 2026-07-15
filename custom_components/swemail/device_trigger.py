"""Device triggers for Swedish Mail Delivery."""

import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import state as state_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PROVIDERS, DOMAIN

TRIGGER_TYPES = {"delivery_today", "delivery_tomorrow"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
    }
)


def _is_combined(unique_id: str) -> bool:
    """Return True for the combined (any provider) binary sensor."""
    return not any(f"_{provider}_" in unique_id for provider in CONF_PROVIDERS)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device triggers for the device."""
    registry = er.async_get(hass)
    triggers: list[dict[str, str]] = []

    for entry in er.async_entries_for_device(registry, device_id):
        if entry.domain != "binary_sensor" or not entry.unique_id:
            continue
        if not _is_combined(entry.unique_id):
            continue
        for trigger_type in TRIGGER_TYPES:
            if entry.unique_id.endswith(f"_{trigger_type}"):
                triggers.append(
                    {
                        CONF_PLATFORM: "device",
                        CONF_DOMAIN: DOMAIN,
                        CONF_DEVICE_ID: device_id,
                        CONF_ENTITY_ID: entry.entity_id,
                        CONF_TYPE: trigger_type,
                    }
                )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger; fires when the backing binary sensor turns on."""
    state_config = {
        CONF_PLATFORM: "state",
        CONF_ENTITY_ID: [config[CONF_ENTITY_ID]],
        state_trigger.CONF_TO: "on",
    }
    state_config = await state_trigger.async_validate_trigger_config(hass, state_config)
    return await state_trigger.async_attach_trigger(
        hass, state_config, action, trigger_info, platform_type="device"
    )
