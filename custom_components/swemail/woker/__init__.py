import logging
from pydoc import resolve
import re
from datetime import datetime
import html
import aiohttp
import asyncio
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

    async def _fetch_data_async(self, url, datatype):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if (datatype=='json'):
                    result = await resp.json()
                else:
                    result = await resp.text()

                return result

    def _fetch_data(self, url):
        r = requests.get(url)
        r.raise_for_status()
        return r

    def _handle_pn_data(self, data,postalcode):
        try:
            arr = data["delivery"].split()
            formattedDate = f"{arr[2]}-{self._dateTable[arr[1]]}-{arr[0].zfill(2)}"

            self._data[CONF_PROVIDER_POSTNORD][data["postalCode"]] = {
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'postal_city': data["city"].capitalize(),
                'next_delivery': formattedDate
            }
        except Exception as error:
                _LOGGER.error(f"Process data failed (PN): {error}")
                self._data[CONF_PROVIDER_POSTNORD][postalcode] = {
                    'last_update': '',
                    'postal_city': '',
                    'next_delivery': ''                    
                }

    def _handle_cm_data(self, data,postalcode):
        try:
            match = re.search(r'<h2>([0-9]{5}) (.*)<\/h2>[\w\W]*>(.*)<\/span>', data)     
            if match:
                self._data[CONF_PROVIDER_CITYMAIL][int(match.group(1))] = {
                    'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'postal_city': html.unescape(match.group(2)).capitalize(),
                    'next_delivery': match.group(3)
                }
        except Exception as error:
                _LOGGER.error(f"Process data failed (CM): {error}")
                self._data[CONF_PROVIDER_CITYMAIL][postalcode] = {
                    'last_update': '',
                    'postal_city': '',
                    'next_delivery': ''                    
                }


    async def fetchPostalCity(self, postalcode):
            data = await self._fetch_data_async(self._URL[CONF_PROVIDER_POSTNORD].format(postalcode),'json')
            return data["city"].capitalize()

    def fetch(self,postalcode,provider):
        data = self._fetch_data(self._URL[provider].format(postalcode))

        if (provider==CONF_PROVIDER_POSTNORD):
            self._handle_pn_data(data.json(),postalcode)

        if (provider==CONF_PROVIDER_CITYMAIL):
            self._handle_cm_data(data.text,postalcode)
