"""Component for wiffi support."""
import logging
from builtins import property
from datetime import timedelta
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_POSTALCODE, CONF_PROVIDERS, DOMAIN
from .woker import HttpWorker

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor"]

async def async_setup(hass, config):
    """Set up HASL integration"""
    
    # SERVICE FUNCTIONS
    @callback
    async def fetch_data(crapdata):
        await hass.async_add_executor_job(hass.data[DOMAIN]._fetch)
        return True

    hass.services.async_register(DOMAIN, 'fetch_data', fetch_data)

    return True

async def async_migrate_entry(hass, config_entry: ConfigEntry):
    return True

async def reload_entry(hass, entry):
    """Reload HASL."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry, config_entry contains data from config entry database."""
    # store worker object
    if (DOMAIN in hass.data):
        worker = hass.data[DOMAIN]
    else:
        worker = hass.data.setdefault(DOMAIN, SweMailDeliveryWorker(hass))

    # add pollen region to worker
    worker.add_entry(entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await hass.async_add_executor_job(worker._fetch)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        worker = hass.data[DOMAIN]
        worker.remove_entry(entry)
        if worker.is_idle():
            # also remove worker if not used by any entry any more
            del hass.data[DOMAIN]

    return unload_ok


class SweMailDeliveryWorker:
    """worker object. Stored in hass.data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the instance."""
        self._hass = hass
        self._worker = HttpWorker()
        self._fetch_callback_listener = None
        self._postalcodes = {}

    @property
    def worker(self):
        return self._worker

    @property
    def postalcodes(self):
        return self._postalcodes

    def add_entry(self, config_entry: ConfigEntry):
        """Add entry."""
        self._hass.bus.fire(f"{DOMAIN}_changed", {"action": "add", "postalcode": config_entry.data[CONF_POSTALCODE]})
        if self.is_idle():
            # This is the first entry, therefore start the timer
            self._fetch_callback_listener = async_track_time_interval(
                self._hass, self._fetch_callback, timedelta(minutes=60)
            )

        self._postalcodes[config_entry.data[CONF_POSTALCODE]] = config_entry

    def remove_entry(self, config_entry: ConfigEntry):
        """Remove entry."""
        self._hass.bus.fire(f"{DOMAIN}_changed", {"action": "remove", "postalcode": config_entry.data[CONF_POSTALCODE]})
        self._postalcodes.pop(config_entry.data[CONF_POSTALCODE])

        if self.is_idle():
            # This was the last region, therefore stop the timer
            remove_listener = self._fetch_callback_listener
            if remove_listener is not None:
                remove_listener()

    def is_idle(self) -> bool:
        return not bool(self._postalcodes)

    @callback
    def _fetch_callback(self, *_):
        self._hass.add_job(self._fetch)

    def _fetch(self, *_):
        for postalcode in self._postalcodes:
            try:
                for provider in CONF_PROVIDERS:
                    if (self._postalcodes[postalcode].data[provider]):
                        self._worker.fetch(postalcode,provider)
                    self._hass.bus.fire(f"{DOMAIN}_changed", {"action": "refresh", "postalcode": postalcode, "provider": provider})
            except Exception as error:
                _LOGGER.error(f"fetch data failed : {error}")
