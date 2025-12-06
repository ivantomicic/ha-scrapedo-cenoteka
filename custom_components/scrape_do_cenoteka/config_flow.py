"""Config flow for Scrape.do - Cenoteka integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CENOTEKA_URL,
    CONF_PRICE_THRESHOLD,
    CONF_SCRAPE_DO_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_CENOTEKA_URL): str,
        vol.Required(CONF_SCRAPE_DO_TOKEN): str,
        vol.Required(CONF_PRICE_THRESHOLD, default=0.0): vol.Coerce(float),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=86400)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Basic validation
    if not data[CONF_CENOTEKA_URL].startswith("https://cenoteka.rs/"):
        raise InvalidUrl("Invalid Cenoteka URL. Must start with https://cenoteka.rs/")

    if data[CONF_PRICE_THRESHOLD] < 0:
        raise InvalidThreshold("Price threshold must be non-negative")

    # Test the connection by making a test request
    # We'll do this in the executor since it's I/O
    try:
        await hass.async_add_executor_job(
            _test_connection, data[CONF_CENOTEKA_URL], data[CONF_SCRAPE_DO_TOKEN]
        )
    except Exception as err:
        raise CannotConnect(f"Cannot connect: {err}") from err

    return {"title": data[CONF_NAME]}


def _test_connection(url: str, token: str) -> None:
    """Test the connection to Scrape.do."""
    import requests

    scrape_url = f"http://api.scrape.do/?url={url}&token={token}&output=raw"
    resp = requests.get(scrape_url, timeout=10)
    resp.raise_for_status()


class CenotekaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Scrape.do - Cenoteka."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidUrl:
                errors[CONF_CENOTEKA_URL] = "invalid_url"
            except InvalidThreshold:
                errors[CONF_PRICE_THRESHOLD] = "invalid_threshold"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    async def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return CenotekaOptionsFlowHandler(config_entry)


class CenotekaOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Scrape.do - Cenoteka."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update options and reload entry
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
                    vol.Optional(
                        CONF_PRICE_THRESHOLD,
                        default=self.config_entry.options.get(
                            CONF_PRICE_THRESHOLD,
                            self.config_entry.data.get(CONF_PRICE_THRESHOLD, 0.0),
                        ),
                    ): vol.Coerce(float),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidUrl(HomeAssistantError):
    """Error to indicate invalid URL."""


class InvalidThreshold(HomeAssistantError):
    """Error to indicate invalid threshold."""

