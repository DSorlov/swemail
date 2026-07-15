"""Provide info to system health."""

import logging

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info, "/config/integrations")


async def system_health_info(hass: HomeAssistant):
    """Get info for the info page."""
    coordinators = hass.data.get(DOMAIN, {})

    return {
        "Version": VERSION,
        "Instances": len(coordinators),
        "Last update success": (
            all(
                coordinator.last_update_success for coordinator in coordinators.values()
            )
            if coordinators
            else False
        ),
    }
