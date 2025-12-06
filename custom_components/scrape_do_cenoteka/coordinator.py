"""Data coordinator for Scrape.do - Cenoteka integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import requests
from bs4 import BeautifulSoup

from .const import (
    ATTR_BELOW_THRESHOLD_COUNT,
    ATTR_LAST_BELOW_THRESHOLD,
    CONF_CENOTEKA_URL,
    CONF_PRICE_THRESHOLD,
    CONF_SCRAPE_DO_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    STORE_NAME_MAP,
)

_LOGGER = logging.getLogger(__name__)


class CenotekaData:
    """Class to hold Cenoteka data."""

    def __init__(self) -> None:
        """Initialize."""
        self.prices_by_store: dict[str, float] = {}
        self.lowest_price: float | None = None
        self.lowest_price_store: str | None = None
        self.price_below_threshold: bool = False
        self.below_threshold_count: int = 0
        self.last_below_threshold: datetime | None = None
        self.update_time: datetime | None = None


class CenotekaCoordinator(DataUpdateCoordinator[CenotekaData]):
    """Coordinator for Cenoteka data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.cenoteka_url = entry.data[CONF_CENOTEKA_URL]
        self.scrape_do_token = entry.data[CONF_SCRAPE_DO_TOKEN]
        self.price_threshold = entry.options.get(
            CONF_PRICE_THRESHOLD, entry.data.get(CONF_PRICE_THRESHOLD, 0.0)
        )
        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> CenotekaData:
        """Fetch data from Cenoteka."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    def _fetch_data(self) -> CenotekaData:
        """Fetch data from Cenoteka (runs in executor)."""
        scrape_url = (
            "http://api.scrape.do/"
            f"?url={self.cenoteka_url}"
            f"&token={self.scrape_do_token}"
            "&output=raw"
        )

        resp = requests.get(scrape_url, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        prices_by_store: dict[str, float] = {}

        rows = soup.select(".bg-white .prices_offline_col .row")

        for row in rows:
            img = row.select_one("img[alt]")
            price_el = row.select_one(".product_price")

            if not img or not price_el:
                continue

            store = img["alt"].strip()
            # Map store name (e.g., Tempo -> Mega Maxi)
            store = STORE_NAME_MAP.get(store, store)

            price_text = price_el.get_text(strip=True)

            try:
                price = float(price_text.replace(".", "").replace(",", "."))
                prices_by_store[store] = price
            except ValueError:
                continue

        data = CenotekaData()
        data.prices_by_store = prices_by_store
        data.update_time = datetime.now()

        if prices_by_store:
            # Find lowest price
            data.lowest_price = min(prices_by_store.values())
            data.lowest_price_store = min(
                prices_by_store, key=prices_by_store.get
            )

            # Check if below threshold
            data.price_below_threshold = (
                data.lowest_price < self.price_threshold
            )

            # Track below threshold count and time
            if data.price_below_threshold:
                # Get previous state
                if hasattr(self, "data") and self.data:
                    data.below_threshold_count = self.data.below_threshold_count
                    # Only increment if it's a new event (wasn't below before)
                    if not self.data.price_below_threshold:
                        data.below_threshold_count += 1
                        data.last_below_threshold = datetime.now()
                    else:
                        data.last_below_threshold = self.data.last_below_threshold
                else:
                    data.below_threshold_count = 1
                    data.last_below_threshold = datetime.now()
            else:
                # Keep previous count and last time if available
                if hasattr(self, "data") and self.data:
                    data.below_threshold_count = self.data.below_threshold_count
                    data.last_below_threshold = self.data.last_below_threshold

        return data

