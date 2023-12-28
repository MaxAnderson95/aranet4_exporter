# Prometheus exporter for the aranet4 CO2 sensor

This is a Prometheus metrics exporter for the [Aranet4](https://aranet4.com/) CO2 sensor. It is written in Python and uses the [Prometheus client library](https://github.com/prometheus/client_python)

The exporter connects to the sensor over bluetooth and exposes the following metrics:

- aranet4_co2
- aranet4_temperature
- aranet4_pressure
- aranet4_humidity
- aranet4_battery_level
- aranet4_update_interval
- aranet4_since_last_update

## Usage

1. Set environment variables to configure the exporter:
    - `POLLING_INTERVAL_SECONDS` how often to poll the sensor (default: 5)
    - `EXPORTER_PORT` port to expose the metrics on (default: 80)
    - `SENSOR_MAC_ADDRESS` MAC address of the sensor to poll. If not set, the exporter will use autodiscovery to find the sensor.

1. Install the dependencies:

    ```shell
    pip install -r requirements.txt
    ```

1. Run the exporter:

    ```shell
    python src/main.py
    ```

1. Scrape the metrics with Prometheus or view them in the browser: `http://localhost:80`

## Notes & credits

- The exporter uses the [pyaranet4](https://github.com/stijnstijn/pyaranet4) library to communicate with the sensor. Currently there is a bug when specifying a MAC address manually, so until [this pr is merged](https://github.com/stijnstijn/pyaranet4/pull/6), i've bundled a forked version of the library in this repo with the fix applied. Thanks stinjnstijn!

- The basic scaffolding of the code for the exporter is based on [Thomas Stringer's example](https://trstringer.com/quick-and-easy-prometheus-exporter/). Thanks Thomas!
