import logging
from re import L
from urllib.request import parse_keqv_list

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (ATTR_IDENTIFIERS, ATTR_MANUFACTURER,
                                 ATTR_MODEL, ATTR_NAME)
from homeassistant.helpers.device_registry import DeviceEntryType
from datetime import datetime

from .const import CONF_POSTALCODE, CONF_PROVIDER_CITYMAIL, CONF_PROVIDER_POSTNORD, DEVICE_AUTHOR, DEVICE_NAME, DOMAIN, CONF_PROVIDERS, DEVICE_VERSION, SENSOR_NAME, SENSOR_ATTRIB

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.   

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    worker = hass.data[DOMAIN].worker
    entities = []

    if (config_entry.options.get(CONF_PROVIDER_POSTNORD)):
        entities.append(ProviderMailDeliverySensor(hass, worker, config_entry.data, CONF_PROVIDER_POSTNORD))

    if (config_entry.options.get(CONF_PROVIDER_CITYMAIL)):
        entities.append(ProviderMailDeliverySensor(hass, worker, config_entry.data, CONF_PROVIDER_CITYMAIL))

    entities.append(NextMailDeliverySensor(hass, worker, config_entry.data))

    async_add_entities(entities)


class ProviderMailDeliverySensor(SensorEntity):
    """Common functionality for all entities."""

    def __init__(self, hass, worker, config, provider):
        self._worker = worker
        self._postalcode = config[CONF_POSTALCODE]
        self._provider = provider
        self._value = None

        self._update_sensor_listener = None

        # set HA instance attributes directly (don't use property)
        self._attr_unique_id = f"{DOMAIN}_{self._postalcode}_{self._provider}"
        self._attr_name = f"{self._provider.capitalize()} {SENSOR_NAME} {self._postalcode}"
        self._attr_icon = "mdi:email-fast-outline"
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: DEVICE_AUTHOR,
            ATTR_MODEL: "v"+DEVICE_VERSION,
            "entry_type": DeviceEntryType.SERVICE,
        }

        

    async def async_update(self):
        """Update the value of the entity."""
        attributes = {}
        provider = self._provider

        if (provider in self._worker.data and self._postalcode in self._worker.data[provider]):
            attributes['next_delivery']= self._worker.data[provider][self._postalcode]['next_delivery']
            attributes['last_update']= self._worker.data[provider][self._postalcode]['last_update']
            attributes['postal_city']= self._worker.data[provider][self._postalcode]['postal_city']
            attributes['logo'] = f"https://logo.clearbit.com/{provider}.se"
            nextDate = datetime.strptime(self._worker.data[provider][self._postalcode]['next_delivery'], "%Y-%m-%d")
            numdays = (nextDate - datetime.now()).days+1
            if (numdays<0):
                self._value = 0
            else:
                self._value = numdays
        else:
            attributes['next_delivery'] = ''
            attributes['last_update'] = ''
            attributes['postal_city'] = ''
            attributes['logo'] = ''
            self._value = None
    
        attributes['provider']= provider
        attributes['postal_code']= self._postalcode
        self._attr_extra_state_attributes = attributes

        self._attr_attribution = SENSOR_ATTRIB

    @property
    def available(self):
        """Return true if value is valid."""
        return self._value is not None

    @property
    def native_value(self):
        """Return the value of the entity."""
        return self._value



class NextMailDeliverySensor(SensorEntity):
    """Common functionality for all entities."""

    def __init__(self, hass, worker, config):
        self._worker = worker
        self._postalcode = config[CONF_POSTALCODE]
        self._providers = []
        self._value = None

        for provider in CONF_PROVIDERS:
            if (config[provider]):
                 self._providers.append(provider) 

        self._update_sensor_listener = None
    
        # set HA instance attributes directly (don't use property)
        self._attr_unique_id = f"{DOMAIN}_{self._postalcode}"
        self._attr_name = f"Mail {SENSOR_NAME} {self._postalcode}"
        self._attr_icon = "mdi:email-fast-outline"
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: DEVICE_AUTHOR,
            ATTR_MODEL: "v"+DEVICE_VERSION,
            "entry_type": DeviceEntryType.SERVICE,
        }

        

    async def async_update(self):
        """Update the value of the entity."""
        attributes = {
            'all_providers': ",".join(self._providers),
        }

        bestDate = None
        bestProvider = None

        for provider in self._providers:
            if (provider in self._worker.data and self._postalcode in self._worker.data[provider]):
                attributes[provider] = {}
                attributes[provider]['next_delivery']= self._worker.data[provider][self._postalcode]['next_delivery']
                attributes[provider]['last_update']= self._worker.data[provider][self._postalcode]['last_update']
                attributes[provider]['postal_city']= self._worker.data[provider][self._postalcode]['postal_city']

                newDate = datetime.strptime(attributes[provider]['next_delivery'], "%Y-%m-%d")
                if (bestDate is None or newDate < bestDate):
                    bestDate = newDate
                    bestProvider = provider

            else:
                attributes[provider] = {}
                attributes[provider]['next_delivery'] = ''
                attributes[provider]['last_update'] = ''
                attributes[provider]['postal_city'] = ''

    
        if (not bestDate is None):
            attributes['next_provider'] = bestProvider.capitalize()
            attributes['next_logo'] = f"https://logo.clearbit.com/{bestProvider}.se"
            attributes['next_date'] = bestDate.strftime("%Y-%m-%d")
            numdays = (bestDate - datetime.now()).days
            if (numdays<0):
                self._value = 0
        else:
            attributes['next_provider'] = ''
            attributes['next_logo'] = ''
            attributes['next_date'] = ''
            self._value = None

        attributes['postal_code']= self._postalcode
        self._attr_extra_state_attributes = attributes

        self._attr_attribution = SENSOR_ATTRIB

    @property
    def available(self):
        """Return true if value is valid."""
        return self._value is not None

    @property
    def native_value(self):
        """Return the value of the entity."""
        return self._value
