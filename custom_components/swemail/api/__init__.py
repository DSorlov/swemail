import asyncio
import html
import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp

try:
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
except ImportError:  # pragma: no cover - allows standalone use/testing
    async_get_clientsession = None

from ..const import CONF_PROVIDER_CITYMAIL, CONF_PROVIDER_POSTNORD

_LOGGER = logging.getLogger(__name__)


class DeliveryDetails:
    def __init__(self, last_update, postal_city, next_delivery):
        self._last_update = last_update
        self._postal_city = postal_city
        self._next_delivery = next_delivery

    def __repr__(self):
        return f"{self.__class__.__name__}(last_update: {self._last_update}, postal_city '{self._postal_city}', next_delivery: {self._next_delivery})"

    @property
    def last_update(self):
        return self._last_update

    @property
    def postal_city(self):
        return self._postal_city

    @property
    def next_delivery(self):
        return self._next_delivery


class HttpWorker:
    _URL = {
        CONF_PROVIDER_CITYMAIL: "https://postnummersok.citymail.se/?search={}",
        CONF_PROVIDER_POSTNORD: "https://portal.postnord.com/api/sendoutarrival/closest?postalCode={}",
    }

    _dateTable = {
        "januari,": "01",
        "februari,": "02",
        "mars,": "03",
        "april,": "04",
        "maj,": "05",
        "juni,": "06",
        "juli,": "07",
        "augusti,": "08",
        "september,": "09",
        "oktober,": "10",
        "november,": "11",
        "december,": "12",
    }

    def __init__(self, hass=None):
        self._hass = hass
        self._data = {CONF_PROVIDER_CITYMAIL: {}, CONF_PROVIDER_POSTNORD: {}}

    @property
    def data(self):
        return self._data

    async def _fetch_data_async(self, url: str, datatype: str = "text") -> Any:
        """Fetch data from URL asynchronously.

        Reuses Home Assistant's shared aiohttp session when available instead of
        creating (and tearing down) a new session on every request.
        """
        timeout = aiohttp.ClientTimeout(total=30)

        if self._hass is not None and async_get_clientsession is not None:
            session = async_get_clientsession(self._hass)
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.json() if datatype == "json" else await resp.text()

        # Fallback for standalone use (e.g. tests) without a hass instance.
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json() if datatype == "json" else await resp.text()

    def _parse_pn_date(self, value: Any) -> str:
        """Parse a PostNord Swedish date string (e.g. "17 juli, 2026").

        Returns an ISO date (YYYY-MM-DD) or an empty string when the value is
        missing, "N/A" or otherwise not parseable (e.g. areas without a
        scheduled date).
        """
        arr = str(value or "").split()
        if len(arr) < 3 or arr[1] not in self._dateTable:
            return ""
        return f"{arr[2]}-{self._dateTable[arr[1]]}-{arr[0].zfill(2)}"

    def _handle_pn_data(self, data: Dict[str, Any], postalcode: int) -> None:
        """Handle PostNord data response."""
        try:
            postal_city = str(data.get("city", "")).capitalize()
            next_delivery = self._parse_pn_date(data.get("delivery"))
            upcoming_delivery = self._parse_pn_date(data.get("upcoming"))

            # PostNord returns an empty/"N/A" delivery for areas without a
            # scheduled date (e.g. the "fasta dagar" pilot). Store empty data
            # instead of spamming the log with errors every update.
            if not next_delivery and data.get("delivery"):
                _LOGGER.debug(
                    "PostNord returned no parseable delivery for %s: %r",
                    postalcode,
                    data.get("delivery"),
                )

            self._data[CONF_PROVIDER_POSTNORD][postalcode] = {
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "postal_city": postal_city,
                "next_delivery": next_delivery,
                "upcoming_delivery": upcoming_delivery,
            }
        except Exception as error:
            _LOGGER.error("Process data failed (PN): %s", error)
            self._data[CONF_PROVIDER_POSTNORD][postalcode] = {
                "last_update": "",
                "postal_city": "",
                "next_delivery": "",
                "upcoming_delivery": "",
            }

    def _handle_cm_data(self, data: str, postalcode: int) -> None:
        """Handle CityMail data response."""
        try:
            city_match = re.search(r"<h2>\s*([0-9]{5})\s+([^<]+?)\s*</h2>", data)
            date_match = re.search(
                r"Nästa utdelningsdag:\s*<span[^>]*>\s*"
                r"([0-9]{4}-[0-9]{2}-[0-9]{2})\s*</span>",
                data,
            )

            if city_match and date_match:
                self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "postal_city": html.unescape(city_match.group(2)).capitalize(),
                    "next_delivery": date_match.group(1),
                    "upcoming_delivery": "",
                }
            else:
                # CityMail does not deliver to this postal code (the page only
                # shows the search form) or the page layout changed.
                _LOGGER.debug("CityMail returned no delivery info for %s", postalcode)
                self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "postal_city": "",
                    "next_delivery": "",
                    "upcoming_delivery": "",
                }
        except Exception as error:
            _LOGGER.error("Process data failed (CM): %s", error)
            self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                "last_update": "",
                "postal_city": "",
                "next_delivery": "",
                "upcoming_delivery": "",
            }

    async def fetch_postal_city(self, postalcode: int) -> str:
        """Fetch postal city name from PostNord API."""
        data = await self._fetch_data_async(
            self._URL[CONF_PROVIDER_POSTNORD].format(postalcode), "json"
        )
        return data["city"].capitalize()

    async def fetch_async(self, postalcode: int, provider: str) -> None:
        """Fetch delivery data for a specific provider asynchronously."""
        try:
            if provider == CONF_PROVIDER_POSTNORD:
                data = await self._fetch_data_async(
                    self._URL[provider].format(postalcode), "json"
                )
                self._handle_pn_data(data, postalcode)
            elif provider == CONF_PROVIDER_CITYMAIL:
                data = await self._fetch_data_async(
                    self._URL[provider].format(postalcode), "text"
                )
                self._handle_cm_data(data, postalcode)
        except Exception as error:
            _LOGGER.error("Fetch failed for %s (%s): %s", provider, postalcode, error)
