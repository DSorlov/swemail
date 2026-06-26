import asyncio
import html
import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
import requests

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

    def __init__(self):
        self._data = {CONF_PROVIDER_CITYMAIL: {}, CONF_PROVIDER_POSTNORD: {}}

    @property
    def data(self):
        return self._data

    def _fetch_data(self, url: str):
        """Synchronous fetch using requests (required by older main components)."""
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r

    async def _fetch_data_async(self, url: str, datatype: str = "text") -> Any:
        """Asynchronous fetch using aiohttp (required by newer components)."""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                if datatype == "json":
                    return await resp.json()
                else:
                    return await resp.text()

    def _handle_pn_data(self, data: Dict[str, Any], postalcode: int) -> None:
        """Handle PostNord data response and safely parse delivery dates."""
        try:
            delivery_text = str(data.get("delivery", "")).strip()
            _LOGGER.debug(
                "PostNord raw delivery string: %s",
                delivery_text,
            )

            # Split the delivery string by whitespace (expected format: "26 juni, 2026")
            arr = delivery_text.split()

            # Ensure the list has at least 3 elements to prevent IndexError
            if len(arr) >= 3:
                day = arr[0].zfill(2)
                # Strip trailing commas to make month lookup safe and resilient
                month_name = arr[1].lower().rstrip(",")
                year = arr[2]

                # Clean the date table keys by stripping trailing commas for safe mapping
                clean_date_table = {
                    k.rstrip(","): v for k, v in self._dateTable.items()
                }
                month = clean_date_table.get(month_name, "01")

                formatted_date = f"{year}-{month}-{day}"
            else:
                # Fallback if the API returns an empty string or an alternative status text
                if delivery_text:
                    _LOGGER.warning(
                        "PostNord returned an unexpected or "
                        "non-parseable format: '%s'",
                        delivery_text,
                    )
                    formatted_date = delivery_text
                else:
                    formatted_date = "No delivery scheduled"

            # Create the payload dictionary
            payload = {
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "postal_city": data["city"].capitalize(),
                "next_delivery": formatted_date,
            }

            # Store using BOTH string and integer keys to prevent silent type-mismatch bugs
            self._data[CONF_PROVIDER_POSTNORD][int(postalcode)] = payload
            self._data[CONF_PROVIDER_POSTNORD][str(postalcode)] = payload

            if "postalCode" in data:
                self._data[CONF_PROVIDER_POSTNORD][str(data["postalCode"])] = payload
                if str(data["postalCode"]).isdigit():
                    self._data[CONF_PROVIDER_POSTNORD][int(data["postalCode"])] = payload

        except Exception as error:
            _LOGGER.error(
                "Process data failed (PN): %s",
                error,
            )
            self._data[CONF_PROVIDER_POSTNORD][postalcode] = {
                "last_update": "",
                "postal_city": "",
                "next_delivery": "",
            }

    def _handle_cm_data(self, data: str, postalcode: int) -> None:
        """Handle CityMail data response."""
        try:
            match = re.search(r"<h2>([0-9]{5}) (.*)<\/h2>[\w\W]*>(.*)<\/span>", data)
            if match:
                self._data[CONF_PROVIDER_CITYMAIL][int(match.group(1))] = {
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "postal_city": html.unescape(match.group(2)).capitalize(),
                    "next_delivery": match.group(3),
                }
        except Exception as error:
            _LOGGER.error(
                "Process data failed (CM): %s",
                error,
            )
            self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                "last_update": "",
                "postal_city": "",
                "next_delivery": "",
            }

    def fetch(self, postalcode: int, provider: str) -> None:
        """Synchronous fetch method used by the main integration component."""
        try:
            res = self._fetch_data(self._URL[provider].format(postalcode))
            if provider == CONF_PROVIDER_POSTNORD:
                self._handle_pn_data(res.json(), postalcode)
            elif provider == CONF_PROVIDER_CITYMAIL:
                self._handle_cm_data(res.text, postalcode)
        except Exception as error:
            _LOGGER.error(
                "Fetch failed for %s (%s): %s",
                provider,
                postalcode,
                error,
            )

    async def fetch_async(self, postalcode: int, provider: str) -> None:
        """Asynchronous fetch method (kept for compatibility)."""
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
            _LOGGER.error(
                "Fetch async failed for %s (%s): %s",
                provider,
                postalcode,
                error,
            )

    async def fetch_postal_city(self, postalcode: int) -> str:
        """Fetch postal city name from PostNord API (snake_case)."""
        data = await self._fetch_data_async(
            self._URL[CONF_PROVIDER_POSTNORD].format(postalcode), "json"
        )
        return data["city"].capitalize()

    async def fetchPostalCity(self, postalcode: int) -> str:
        """Fetch postal city name from PostNord API (camelCase alias)."""
        return await self.fetch_postal_city(postalcode)
