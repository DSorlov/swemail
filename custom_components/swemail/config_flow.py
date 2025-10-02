"""Config flow"""

import logging

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import callback

from .const import (
    CONF_POSTALCODE,
    CONF_PROVIDER_CITYMAIL,
    CONF_PROVIDER_POSTNORD,
    DOMAIN,
)
from .woker import HttpWorker

_LOGGER = logging.getLogger(__name__)


class InvalidPostalCode(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


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
                vol.Required(CONF_POSTALCODE, default="10000"): vol.All(
                    vol.Coerce(int), vol.Range(min=10000, max=99999)
                ),
                vol.Optional(CONF_PROVIDER_POSTNORD, default=True): bool,
                vol.Optional(CONF_PROVIDER_CITYMAIL, default=True): bool,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=data_schema)
        else:

            error_schema = vol.Schema(
                {
                    vol.Required(
                        CONF_POSTALCODE, default=user_input[CONF_POSTALCODE]
                    ): vol.All(vol.Coerce(int), vol.Range(min=10000, max=99999)),
                    vol.Optional(
                        CONF_PROVIDER_POSTNORD,
                        default=user_input[CONF_PROVIDER_POSTNORD],
                    ): bool,
                    vol.Optional(
                        CONF_PROVIDER_CITYMAIL,
                        default=user_input[CONF_PROVIDER_CITYMAIL],
                    ): bool,
                }
            )

            try:
                postalcode = user_input[CONF_POSTALCODE]
                postalCity = await HttpWorker().fetch_postal_city(postalcode)
            except Exception:
                return self.async_show_form(
                    step_id="user",
                    data_schema=error_schema,
                    errors={"base": "invalid_postcode"},
                )

            try:
                entryTitle = f"{postalCity} {postalcode}"
                unique_id = f"{DOMAIN} {postalcode}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=entryTitle,
                    data={
                        CONF_POSTALCODE: postalcode,
                        CONF_PROVIDER_POSTNORD: user_input[CONF_PROVIDER_POSTNORD],
                        CONF_PROVIDER_CITYMAIL: user_input[CONF_PROVIDER_CITYMAIL],
                    },
                )
            except Exception:
                return self.async_show_form(
                    step_id="user",
                    data_schema=error_schema,
                    errors={"base": "creation_error"},
                )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SweMailDeliveryOptionsFlow(config_entry)


class SweMailDeliveryOptionsFlow(config_entries.OptionsFlow):
    """HASL config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HASL options flow."""
        super().__init__()
        self._config_entry = config_entry

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
                vol.Optional(
                    CONF_PROVIDER_POSTNORD,
                    default=self._config_entry.data.get(CONF_PROVIDER_POSTNORD),
                ): bool,
                vol.Optional(
                    CONF_PROVIDER_CITYMAIL,
                    default=self._config_entry.data.get(CONF_PROVIDER_CITYMAIL),
                ): bool,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=data_schema)
        else:
            postalcode = self._config_entry.data[CONF_POSTALCODE]

            postalCity = await HttpWorker().fetch_postal_city(postalcode)
            entryTitle = f"{postalCity} {postalcode}"

            return self.async_create_entry(
                title=entryTitle,
                data={
                    CONF_POSTALCODE: postalcode,
                    CONF_PROVIDER_POSTNORD: user_input[CONF_PROVIDER_POSTNORD],
                    CONF_PROVIDER_CITYMAIL: user_input[CONF_PROVIDER_CITYMAIL],
                },
            )
