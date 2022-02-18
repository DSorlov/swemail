"""Constants for the component."""

# Component domain, used to store component data in hass data.
__version__ = "1.0.1"
VERSION = __version__
DOMAIN = "swemail"

SENSOR_NAME = "Delivery"

DEVICE_NAME = "Mail Delivery API"
DEVICE_AUTHOR = "Daniel Sörlöv"
DEVICE_VERSION = __version__

CONF_POSTALCODE = "postalcode"

CONF_PROVIDER_POSTNORD = "postnord"
CONF_PROVIDER_CITYMAIL = "citymail"
CONF_PROVIDERS = [CONF_PROVIDER_POSTNORD, CONF_PROVIDER_CITYMAIL]

SENSOR_ATTRIB = "Data from Postnord and Citymail"

