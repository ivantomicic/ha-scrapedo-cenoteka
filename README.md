# Scrape.do - Cenoteka Integration for Home Assistant

A Home Assistant integration that monitors product prices from Cenoteka.rs using Scrape.do API.

## Features

-   Monitor product prices from Cenoteka.rs
-   Track lowest price across all stores
-   Alert when price drops below threshold
-   Store prices for each retailer (displayed as sensor attributes)
-   Rename "Tempo" stores to "Mega Maxi"
-   Track how often price went below threshold
-   Manual price update service
-   Configurable update interval

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click the three dots menu and select "Custom repositories"
4. Add this repository URL and select category "Integration"
5. The integration should appear in HACS
6. Click "Download" and restart Home Assistant

### Manual Installation

1. Copy the `custom_components/scrape_do_cenoteka` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Scrape.do - Cenoteka"

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Scrape.do - Cenoteka"
3. Fill in the configuration:
    - **Device Name**: A friendly name for this product (e.g., "Salto Pale Ale")
    - **Cenoteka Product URL**: The full URL to the product page (e.g., `https://cenoteka.rs/p/salto-pale-ale-033l/`)
    - **Scrape.do API Token**: Your Scrape.do API token
    - **Price Threshold**: Alert when price drops below this value (in RSD)
    - **Update Interval**: How often to check prices in seconds (default: 3600 = 1 hour, min: 60, max: 86400)

## Sensors

Each configured product creates two sensors:

### Lowest Price

-   Shows the lowest price found across all stores
-   Unit: RSD
-   Attributes:
    -   `store_prices`: Dictionary of all store prices
    -   `lowest_price_store`: Name of the store with the lowest price
    -   `update_time`: Last update timestamp

### Price Below Threshold

-   Shows "on" when the lowest price is below the threshold, "off" otherwise
-   Attributes:
    -   `lowest_price`: Current lowest price
    -   `below_threshold_count`: Number of times price has gone below threshold
    -   `last_below_threshold`: Timestamp of the last time price went below threshold
    -   `update_time`: Last update timestamp

## Services

### scrape_do_cenoteka.update_prices

Manually trigger a price update for a specific product.

**Service Data:**

-   `entity_id` (required): Entity ID of any sensor for the product (e.g., `sensor.salto_pale_ale_lowest_price`)

**Example:**

```yaml
service: scrape_do_cenoteka.update_prices
data:
    entity_id: sensor.salto_pale_ale_lowest_price
```

## Example Automation

Get notified when price drops below threshold:

```yaml
automation:
    - alias: "Price Alert - Salto Pale Ale"
      trigger:
          - platform: state
            entity_id: sensor.salto_pale_ale_price_below_threshold
            to: "on"
      action:
          - service: notify.mobile_app_your_phone
            data:
                title: "Price Alert!"
                message: "{{ state_attr('sensor.salto_pale_ale_lowest_price', 'lowest_price_store') }} has the lowest price: {{ states('sensor.salto_pale_ale_lowest_price') }} RSD"
```

## Requirements

-   BeautifulSoup4 4.12.2
-   lxml 4.9.3
-   requests 2.31.0

These are automatically installed when the integration is installed.

## Support

For issues, feature requests, or contributions, please open an issue on GitHub.

## License

This integration is provided as-is for use with Home Assistant.
