"""Config flow for PVNode integration."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_ORIENTATION,
    CONF_SLOPE,
    CONF_KWP,
    DOMAIN,
)

RE_API_KEY = re.compile(r"^pvn_[a-zA-Z0-9]{32}$")


class PVNodeFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PVNode."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry,) -> PVNodeOptionFlowHandler:
        """Get the options flow for this handler."""
        return PVNodeOptionFlowHandler()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_LATITUDE: user_input[CONF_LATITUDE],
                    CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                },
                options={
                    CONF_ORIENTATION: user_input[CONF_ORIENTATION],
                    CONF_SLOPE: user_input[CONF_SLOPE],
                    CONF_KWP: user_input[CONF_KWP],
                    CONF_API_KEY: user_input[CONF_API_KEY],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY, default=""
                    ): str,
                    vol.Required(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Required(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Required(CONF_SLOPE, default=30): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=90)
                    ),
                    vol.Required(CONF_ORIENTATION, default=180): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=360)
                    ),
                    vol.Required(CONF_KWP): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                }
            ),
        )


class PVNodeOptionFlowHandler(OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options."""
        errors = {}
        if user_input is not None:
            if (api_key := user_input.get(CONF_API_KEY)) and RE_API_KEY.match(api_key) is None:
                errors[CONF_API_KEY] = "invalid_api_key"
            else:
                return self.async_create_entry(title="", data=user_input | {CONF_API_KEY: api_key or None})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_API_KEY, ""
                            )
                        },
                    ): str,
                    vol.Required(
                        CONF_SLOPE,
                        default=self.config_entry.options[CONF_SLOPE],
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=90)),
                    vol.Required(
                        CONF_ORIENTATION,
                        default=self.config_entry.options.get(CONF_ORIENTATION),
                    ): vol.All(vol.Coerce(int), vol.Range(min=-0, max=360)),
                    vol.Required(
                        CONF_KWP,
                        default=self.config_entry.options[CONF_KWP],
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
            errors=errors,
        )