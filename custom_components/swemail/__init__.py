"""Swedish Mail Delivery Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import CONF_POSTALCODE, CONF_PROVIDERS, DOMAIN
from .coordinator import SweMailCoordinator

_LOGGER = logging.getLogger(__name__)

# Configuration schema - integration can only be set up via config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]


async def async_setup(hass, config):
    """Set up the Swedish Mail Delivery integration."""

    # SERVICE FUNCTIONS
    async def fetch_data(call):
        """Service to manually refresh data for all coordinators."""
        if DOMAIN in hass.data:
            for coordinator in hass.data[DOMAIN].values():
                await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "fetch_data", fetch_data)

    return True


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    return True


async def reload_entry(hass, entry):
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry."""

    # Migration from v1.x to v2.x - ensure clean upgrade
    if entry.version < 2:
        _LOGGER.info("Migrating config entry from version %s to 2", entry.version)
        hass.config_entries.async_update_entry(entry, version=2)

    postal_code = entry.data[CONF_POSTALCODE]
    # Options (when set) override the initial config data so provider changes
    # made via the options flow actually take effect after a reload.
    settings = {**entry.data, **entry.options}
    enabled_providers = [
        provider for provider in CONF_PROVIDERS if settings.get(provider, False)
    ]

    # Create coordinator
    coordinator = SweMailCoordinator(hass, postal_code, enabled_providers)

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry when its options change (e.g. extra sensors toggle).
    entry.async_on_unload(entry.add_update_listener(reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Remove coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return unload_ok
