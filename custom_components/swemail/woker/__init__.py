import logging
import re
from datetime import datetime
import html
import aiohttp
import asyncio
from typing import Dict, Any, Optional

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
        CONF_PROVIDER_POSTNORD: "https://portal.postnord.com/api/sendoutarrival/closest?postalCode={}"
        }

    _dateTable = {
        'januari,': '01',
        'februari,': '02',
        'mars,': '03',
        'april,': '04',
        'maj,': '05',
        'juni,': '06',
        'juli,': '07',
        'augusti,': '08',
        'september,': '09',
        'oktober,': '10',
        'november,': '11',
        'december,': '12',
    }

    def __init__(self):
        self._data = {
            CONF_PROVIDER_CITYMAIL: {},
            CONF_PROVIDER_POSTNORD: {}
        }

    @property
    def data(self):
        return self._data

    async def _fetch_data_async(self, url: str, datatype: str = 'text') -> Any:
        """Fetch data from URL asynchronously."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                if datatype == 'json':
                    return await resp.json()
                else:
                    return await resp.text()

    def _handle_pn_data(self, data: Dict[str, Any], postalcode: int) -> None:
        """Handle PostNord data response."""
        try:
            arr = data["delivery"].split()
            formatted_date = f"{arr[2]}-{self._dateTable[arr[1]]}-{arr[0].zfill(2)}"

            self._data[CONF_PROVIDER_POSTNORD][data["postalCode"]] = {
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'postal_city': data["city"].capitalize(),
                'next_delivery': formatted_date
            }
        except Exception as error:
            _LOGGER.error("Process data failed (PN): %s", error)
            self._data[CONF_PROVIDER_POSTNORD][postalcode] = {
                'last_update': '',
                'postal_city': '',
                'next_delivery': ''                    
            }

    def _handle_cm_data(self, data: str, postalcode: int) -> None:
        """Handle CityMail data response."""
        try:
            match = re.search(r'<h2>([0-9]{5}) (.*)<\/h2>[\w\W]*>(.*)<\/span>', data)     
            if match:
                self._data[CONF_PROVIDER_CITYMAIL][int(match.group(1))] = {
                    'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'postal_city': html.unescape(match.group(2)).capitalize(),
                    'next_delivery': match.group(3)
                }
        except Exception as error:
            _LOGGER.error("Process data failed (CM): %s", error)
            self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                'last_update': '',
                'postal_city': '',
                'next_delivery': ''                    
            }


    async def fetch_postal_city(self, postalcode: int) -> str:
        """Fetch postal city name from PostNord API."""
        data = await self._fetch_data_async(self._URL[CONF_PROVIDER_POSTNORD].format(postalcode), 'json')
        return data["city"].capitalize()

    async def fetch_async(self, postalcode: int, provider: str) -> None:
        """Fetch delivery data for a specific provider asynchronously."""
        try:
            if provider == CONF_PROVIDER_POSTNORD:
                data = await self._fetch_data_async(self._URL[provider].format(postalcode), 'json')
                self._handle_pn_data(data, postalcode)
            elif provider == CONF_PROVIDER_CITYMAIL:
                data = await self._fetch_data_async(self._URL[provider].format(postalcode), 'text')
                self._handle_cm_data(data, postalcode)
        except Exception as error:
            _LOGGER.error("Fetch failed for %s (%s): %s", provider, postalcode, error)
