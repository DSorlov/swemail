"""Constants for the component."""

# Component domain, used to store component data in hass data.
__version__ = "2.1.1"
VERSION = __version__
DOMAIN = "swemail"

SENSOR_NAME = "Delivery"

DEVICE_NAME = "Mail Delivery API"
DEVICE_AUTHOR = "Daniel Sörlöv"
DEVICE_VERSION = __version__

CONF_POSTALCODE = "postalcode"
CONF_TITLE = "title"

CONF_PROVIDER_POSTNORD = "postnord"
CONF_PROVIDER_CITYMAIL = "citymail"
CONF_PROVIDERS = [CONF_PROVIDER_POSTNORD, CONF_PROVIDER_CITYMAIL]

# When enabled, additional first-class sensors (next delivery date and postal
# city) are created per provider in addition to the classic days-left sensors.
CONF_EXTRA_SENSORS = "extra_sensors"

# Home Assistant events fired by the coordinator.
EVENT_DELIVERY_TODAY = f"{DOMAIN}_delivery_today"
EVENT_NEXT_DELIVERY_CHANGED = f"{DOMAIN}_next_delivery_changed"

SENSOR_ATTRIB = "Data from Postnord and Citymail"
