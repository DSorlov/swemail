"""Data update coordinator for Swedish Mail Delivery."""

import asyncio
import logging
from datetime import date, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    EVENT_DELIVERY_TODAY,
    EVENT_NEXT_DELIVERY_CHANGED,
)
from .api import HttpWorker

_LOGGER = logging.getLogger(__name__)


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
        self.worker = HttpWorker(hass)
        # Remember the last seen next delivery per provider to detect changes.
        self._previous: dict[str, str] = {}

    async def _async_update_data(self):
        """Fetch data from API endpoints."""
        try:
            # Fetch data for all enabled providers concurrently
            tasks = []
            for provider in self.providers:
                tasks.append(self.worker.fetch_async(self.postal_code, provider))

            await asyncio.gather(*tasks)
            data = self.worker.data
            self._fire_events(data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _fire_events(self, data: dict) -> None:
        """Fire Home Assistant events on delivery date transitions."""
        today = date.today().isoformat()

        for provider in self.providers:
            provider_data = data.get(provider, {}).get(self.postal_code, {})
            next_delivery = provider_data.get("next_delivery") or ""
            previous = self._previous.get(provider)

            # Only fire once we have a baseline, to avoid firing on restart.
            if previous is not None:
                if next_delivery and next_delivery != previous:
                    self.hass.bus.async_fire(
                        EVENT_NEXT_DELIVERY_CHANGED,
                        {
                            "postal_code": self.postal_code,
                            "provider": provider,
                            "next_delivery": next_delivery,
                            "previous": previous,
                        },
                    )
                if next_delivery == today and previous != today:
                    self.hass.bus.async_fire(
                        EVENT_DELIVERY_TODAY,
                        {
                            "postal_code": self.postal_code,
                            "provider": provider,
                            "next_delivery": next_delivery,
                        },
                    )

            self._previous[provider] = next_delivery

