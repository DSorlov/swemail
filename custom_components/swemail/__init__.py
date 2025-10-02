"""Swedish Mail Delivery Integration."""

import logging
from datetime import timedelta
import asyncio
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import CONF_POSTALCODE, CONF_PROVIDERS, DOMAIN
from .woker import HttpWorker

_LOGGER = logging.getLogger(__name__)

# Configuration schema - integration can only be set up via config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["sensor"]


class SweMailCoordinator(DataUpdateCoordinator):
    """Data coordinator for Swedish Mail delivery."""

    def __init__(self, hass: HomeAssistant, postal_code: int, providers: list):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.postal_code = postal_code
        self.providers = providers
        self.worker = HttpWorker()

    async def _async_update_data(self):
        """Fetch data from API endpoints."""
        try:
            # Fetch data for all enabled providers concurrently
            tasks = []
            for provider in self.providers:
                tasks.append(self.worker.fetch_async(self.postal_code, provider))

            await asyncio.gather(*tasks)
            return self.worker.data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


async def async_setup(hass, config):
    """Set up HASL integration"""

    # Register static files for logos
    integration_dir = os.path.dirname(__file__)
    hass.http.register_static_path(
        f"/local/{DOMAIN}", integration_dir, cache_headers=True
    )

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
    """Reload HASL."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry."""
    postal_code = entry.data[CONF_POSTALCODE]
    enabled_providers = [
        provider for provider in CONF_PROVIDERS if entry.data.get(provider, False)
    ]

    # Create coordinator
    coordinator = SweMailCoordinator(hass, postal_code, enabled_providers)

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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
