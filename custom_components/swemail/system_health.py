"""Provide info to system health."""
import sys
import logging

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    VERSION
)

_LOGGER = logging.getLogger(__name__)


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""

    try:
        register.domain = DOMAIN
        register.async_register_info(system_health_info, "/config/integrations")
        _LOGGER.debug("System health registration succeeded")
    except:
        _LOGGER.error("System health registration failed")


async def system_health_info(hass):
    """Get info for the info page."""
    worker = hass.data[DOMAIN]

    try:
        statusObject = {
            "Version": VERSION,
            "Idle": worker.is_idle(),
            "Instances": len(worker.postalcodes)
        }
        _LOGGER.debug("Information gather succeeded")
        return statusObject
    except:
        _LOGGER.debug("Information gather Failed")
        return {
            "Version": VERSION,
            "Idle": "(worker failed)",
            "Instances": "(worker failed)"
        }
