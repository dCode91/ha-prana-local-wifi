"""Config flow for Prana Recuperator integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PranaApiClient, PranaApiError, PranaConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default="Prana Recuperator"): str,
    }
)


async def validate_input(hass, host: str) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = PranaApiClient(host, session=session)

    try:
        state = await api.test_connection()
        return {"title": f"Prana ({host})"}
    finally:
        # Don't close session as it belongs to Home Assistant
        pass


class PranaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Prana Recuperator."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._name: str | None = None
        self._discovered_host: str | None = None
        self._discovered_name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME, "Prana Recuperator")

            # Check if already configured
            self._async_abort_entries_match({CONF_HOST: host})

            try:
                info = await validate_input(self.hass, host)
            except PranaConnectionError:
                errors["base"] = "cannot_connect"
            except PranaApiError:
                errors["base"] = "unknown"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.host
        name = discovery_info.properties.get("label", "Prana Recuperator")

        _LOGGER.debug(
            "Discovered Prana device: host=%s, name=%s, properties=%s",
            host,
            name,
            discovery_info.properties,
        )

        # Set unique ID based on host
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered_host = host
        self._discovered_name = name

        # Try to connect to verify device
        try:
            await validate_input(self.hass, host)
        except (PranaConnectionError, PranaApiError):
            return self.async_abort(reason="cannot_connect")

        self.context["title_placeholders"] = {"name": name}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle confirmation of discovered device."""
        if user_input is not None:
            name = user_input.get(CONF_NAME, self._discovered_name)
            return self.async_create_entry(
                title=name,
                data={
                    CONF_HOST: self._discovered_host,
                    CONF_NAME: name,
                },
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self._discovered_name
                    ): str,
                }
            ),
            description_placeholders={
                "host": self._discovered_host,
                "name": self._discovered_name,
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return PranaOptionsFlow(config_entry)


class PranaOptionsFlow(config_entries.OptionsFlow):
    """Handle Prana options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME,
                        default=self.config_entry.data.get(
                            CONF_NAME, "Prana Recuperator"
                        ),
                    ): str,
                }
            ),
        )
