"""Constants for Scrape.do - Cenoteka integration."""
from __future__ import annotations

DOMAIN = "scrape_do_cenoteka"
ATTRIBUTION = "Data provided by Cenoteka via Scrape.do"

# Configuration keys
CONF_CENOTEKA_URL = "cenoteka_url"
CONF_SCRAPE_DO_TOKEN = "scrape_do_token"
CONF_PRICE_THRESHOLD = "price_threshold"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour
DEFAULT_NAME = "Cenoteka Product"

# Attributes
ATTR_LOWEST_PRICE = "lowest_price"
ATTR_PRICE_BELOW_THRESHOLD = "price_below_threshold"
ATTR_STORE_PRICES = "store_prices"
ATTR_BELOW_THRESHOLD_COUNT = "below_threshold_count"
ATTR_LAST_BELOW_THRESHOLD = "last_below_threshold"
ATTR_UPDATE_TIME = "update_time"

# Service
SERVICE_UPDATE_PRICES = "update_prices"

# Store name mapping
STORE_NAME_MAP = {
    "Tempo": "Mega Maxi"
}

