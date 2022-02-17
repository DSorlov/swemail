"""Config flow"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_POSTALCODE, DOMAIN, CONF_PROVIDER_POSTNORD, CONF_PROVIDER_CITYMAIL

class SweMailDeliveryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Component config flow."""

    VERSION = 1

    # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)
    async def validate_input(self, data):
        """Validate input in step user"""
        return data

    async def async_step_user(self, user_input=None):
   
        data_schema = vol.Schema(
            {
                vol.Required(CONF_POSTALCODE, default="10000"): vol.All(vol.Coerce(int), vol.Range(min=10000, max=99999)),
                vol.Optional(CONF_PROVIDER_POSTNORD, default=True): bool,
                vol.Optional(CONF_PROVIDER_CITYMAIL, default=True): bool
            }
        )

        if (user_input is None):
            return self.async_show_form(step_id="user", data_schema=data_schema)
        else:
            postalcode = user_input[CONF_POSTALCODE]
            unique_id = f"{DOMAIN} {postalcode}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=postalcode, data={CONF_POSTALCODE: postalcode,
                                        CONF_PROVIDER_POSTNORD: user_input[CONF_PROVIDER_POSTNORD],
                                        CONF_PROVIDER_CITYMAIL: user_input[CONF_PROVIDER_CITYMAIL]}
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SweMailDeliveryOptionsFlow(config_entry)            


class SweMailDeliveryOptionsFlow(config_entries.OptionsFlow):
    """HASL config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HASL options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def validate_input(self, data):
        """Validate input in step user"""
        # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)
        return data

    async def async_step_user(self, user_input=None):
   
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_PROVIDER_POSTNORD, default=self.config_entry.options.get(CONF_PROVIDER_POSTNORD)): bool,
                vol.Optional(CONF_PROVIDER_CITYMAIL, default=self.config_entry.options.get(CONF_PROVIDER_CITYMAIL)): bool
            }
        )

        if (user_input is None):
            return self.async_show_form(step_id="user", data_schema=data_schema)
        else:
            postalcode = self.config_entry.data[CONF_POSTALCODE]
            return self.async_create_entry(
                title=postalcode, data={CONF_POSTALCODE: postalcode,
                                        CONF_PROVIDER_POSTNORD: user_input[CONF_PROVIDER_POSTNORD],
                                        CONF_PROVIDER_CITYMAIL: user_input[CONF_PROVIDER_CITYMAIL]}
            )
