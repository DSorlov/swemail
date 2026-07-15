"""Diagnostics support for Swedish Mail Delivery."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_POSTALCODE, DOMAIN

TO_REDACT = {CONF_POSTALCODE}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "config_entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "coordinator": {
            "providers": coordinator.providers,
            "last_update_success": coordinator.last_update_success,
            "data": coordinator.data,
        },
    }
