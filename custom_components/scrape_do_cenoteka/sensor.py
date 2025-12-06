"""Sensor platform for Scrape.do - Cenoteka integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import StateType

from .const import (
    ATTR_BELOW_THRESHOLD_COUNT,
    ATTR_LAST_BELOW_THRESHOLD,
    ATTR_LOWEST_PRICE,
    ATTR_PRICE_BELOW_THRESHOLD,
    ATTR_STORE_PRICES,
    ATTR_UPDATE_TIME,
    DOMAIN,
)
from .coordinator import CenotekaCoordinator, CenotekaData

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="lowest_price",
        name="Lowest Price",
        native_unit_of_measurement="RSD",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="price_below_threshold",
        name="Price Below Threshold",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Scrape.do - Cenoteka sensor from a config entry."""
    coordinator: CenotekaCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            CenotekaSensor(coordinator, description, entry)
            for description in SENSOR_TYPES
        ]
    )


class CenotekaSensor(CoordinatorEntity[CenotekaCoordinator], SensorEntity):
    """Representation of a Cenoteka sensor."""

    def __init__(
        self,
        coordinator: CenotekaCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"{entry.data.get('name', 'Cenoteka Product')} {description.name}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data: CenotekaData | None = self.coordinator.data

        if data is None:
            return None

        if self.entity_description.key == "lowest_price":
            return data.lowest_price

        if self.entity_description.key == "price_below_threshold":
            return "on" if data.price_below_threshold else "off"

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        data: CenotekaData | None = self.coordinator.data

        if data is None:
            return {}

        attrs: dict[str, Any] = {}

        if self.entity_description.key == "lowest_price":
            # Add store prices as attributes
            if data.prices_by_store:
                attrs[ATTR_STORE_PRICES] = data.prices_by_store
                if data.lowest_price_store:
                    attrs["lowest_price_store"] = data.lowest_price_store

        if data.update_time:
            attrs[ATTR_UPDATE_TIME] = data.update_time.isoformat()

        if self.entity_description.key == "price_below_threshold":
            attrs[ATTR_LOWEST_PRICE] = data.lowest_price
            attrs[ATTR_BELOW_THRESHOLD_COUNT] = data.below_threshold_count
            if data.last_below_threshold:
                attrs[ATTR_LAST_BELOW_THRESHOLD] = data.last_below_threshold.isoformat()

        return attrs

