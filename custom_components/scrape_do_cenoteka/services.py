"""Services for Scrape.do - Cenoteka integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, SERVICE_UPDATE_PRICES

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Scrape.do - Cenoteka."""

    async def update_prices(call: ServiceCall) -> None:
        """Service to manually update prices for a Cenoteka device."""
        entity_id = call.data.get("entity_id")

        if not entity_id:
            _LOGGER.error("entity_id is required")
            return

        # Find the config entry for this entity
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)

        if not entity or entity.platform != DOMAIN:
            _LOGGER.error("Entity %s not found or not a Cenoteka entity", entity_id)
            return

        # Find coordinator for this entry
        entry_id = entity.config_entry_id
        if entry_id not in hass.data[DOMAIN]:
            _LOGGER.error("Config entry %s not found", entry_id)
            return

        coordinator = hass.data[DOMAIN][entry_id]
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_UPDATE_PRICES, update_prices)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Scrape.do - Cenoteka."""
    if hass.services.has_service(DOMAIN, SERVICE_UPDATE_PRICES):
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_PRICES)

