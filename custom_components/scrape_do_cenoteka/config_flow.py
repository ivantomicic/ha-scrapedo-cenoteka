"""Config flow for Scrape.do - Cenoteka integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow
try:
    from homeassistant.config_entries import ConfigFlowResult
except ImportError:
    # For older Home Assistant versions (< 2022.8)
    ConfigFlowResult = dict[str, Any]
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidUrl(HomeAssistantError):
    """Error to indicate invalid URL."""


class InvalidThreshold(HomeAssistantError):
    """Error to indicate invalid threshold."""

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
    url = data.get(CONF_CENOTEKA_URL, "")
    if not url or not url.startswith("https://cenoteka.rs/"):
        raise InvalidUrl("Invalid Cenoteka URL. Must start with https://cenoteka.rs/")

    threshold = data.get(CONF_PRICE_THRESHOLD, 0.0)
    if threshold < 0:
        raise InvalidThreshold("Price threshold must be non-negative")

    token = data.get(CONF_SCRAPE_DO_TOKEN, "")
    if not token:
        raise CannotConnect("Scrape.do token is required")

    # Optionally test the connection - skip for now to avoid blocking
    # The actual connection will be tested when the coordinator tries to fetch data

    return {"title": data.get(CONF_NAME, DEFAULT_NAME)}


def _test_connection(url: str, token: str) -> None:
    """Test the connection to Scrape.do."""
    try:
        import requests
    except ImportError:
        raise CannotConnect("requests library not available")

    scrape_url = f"http://api.scrape.do/?url={url}&token={token}&output=raw"
    try:
        resp = requests.get(scrape_url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise CannotConnect(f"Connection failed: {err}") from err


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

