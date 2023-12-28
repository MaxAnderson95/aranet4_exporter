import time
import os
import logging
from pyaranet4 import Aranet4
from pyaranet4.exceptions import Aranet4Exception
from bleak.exc import BleakError
from prometheus_client import start_http_server, Gauge, Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NAN = float("nan")
METRIC_NAMESPACE = "aranet4"


class AranetMetrics:
    def __init__(self, polling_interval_seconds: int = 0, sensor_mac_address: str | None = None) -> None:
        self.polling_interval_seconds = polling_interval_seconds
        self.sensor_mac_address = sensor_mac_address
        self._connected = False

        if self.sensor_mac_address:
            logger.info(f"Connecting with manually specified sensor MAC address {self.sensor_mac_address}")
        else:
            logger.info("Sensor MAC address not specified, will try to auto-discover sensor")

        # Metrics to be exposed
        self.co2 = Gauge("co2", "CO2 concentration in ppm", namespace=METRIC_NAMESPACE)
        self.temperature = Gauge("temperature", "Temperature in Celsius", namespace=METRIC_NAMESPACE)
        self.pressure = Gauge("pressure", "Pressure in hPa", namespace=METRIC_NAMESPACE)
        self.humidity = Gauge("humidity", "Relative humidity in percent", namespace=METRIC_NAMESPACE)
        self.battery_level = Gauge("battery_level", "Battery level in percent", namespace=METRIC_NAMESPACE)
        self.update_interval = Gauge("update_interval", "Update interval in seconds", namespace=METRIC_NAMESPACE)
        self.since_last_update = Gauge("since_last_update", "Seconds since last update", namespace=METRIC_NAMESPACE)
        self.sensor_connected = Enum("connected_to_sensor", "Connected to sensor", namespace=METRIC_NAMESPACE, states=["true", "false"])

    def run_metrics_loop(self) -> None:
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self) -> None:
        try:
            if not self._connected:
                self._aranet = Aranet4(mac_address=self.sensor_mac_address)
                self._connected = True
            if self._aranet:
                readings = self._aranet.current_readings
            else:
                raise ConnectionError("No sensor connected")
        except (Exception, Aranet4Exception) as e:
            logger.error(f"Failed to fetch readings from sensor: {e}")
            self._connected = False
            self._aranet = None
            self.co2.set(NAN)
            self.temperature.set(NAN)
            self.pressure.set(NAN)
            self.humidity.set(NAN)
            self.battery_level.set(NAN)
            self.update_interval.set(NAN)
            self.since_last_update.set(NAN)
            self.sensor_connected.state("false")
            return

        logger.info(f"Readings: {readings}")

        self.co2.set(readings.co2)
        self.temperature.set(readings.temperature)
        self.pressure.set(readings.pressure)
        self.humidity.set(readings.humidity)
        self.battery_level.set(readings.battery_level)
        self.update_interval.set(readings.update_interval)
        self.since_last_update.set(readings.since_last_update)
        self.sensor_connected.state("true")


def main():
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "80"))
    sensor_mac_address = os.getenv("SENSOR_MAC_ADDRESS", None)
    aranet_metrics = AranetMetrics(polling_interval_seconds, sensor_mac_address)
    logger.info(f"Starting exporter on port {exporter_port}, polling interval {polling_interval_seconds} seconds")
    start_http_server(exporter_port)
    aranet_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()
