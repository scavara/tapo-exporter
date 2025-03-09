from contextlib import contextmanager
from enum import Enum, auto
from math import floor
from time import time
from time import sleep

from loguru import logger
from prometheus_client import Histogram
from prometheus_client.core import GaugeMetricFamily
from PyP100 import PyP100


OBSERVATION_RED_METRICS = Histogram(
    "tapo_p100_observation_rate_ms",
    "RED metrics for queries to the TP-Link TAPO P110 devices. (milliseconds)",
    labelnames=["ip_address", "room", "success"],
    buckets=(10, 100, 150, 200, 250, 300, 500, 750, 1000, 1500, 2000)
)


class MetricType(Enum):
    DEVICE_COUNT = auto()
    TODAY_RUNTIME = auto()
    MONTH_RUNTIME = auto()
    TODAY_ENERGY = auto()
    MONTH_ENERGY = auto()
    CURRENT_POWER = auto()


def get_metrics():
    return {
        MetricType.DEVICE_COUNT: GaugeMetricFamily(
            "tapo_p100_device_count",
            "Number of available TP-Link TAPO P110 Smart Sockets.",
        ),
        MetricType.TODAY_RUNTIME: GaugeMetricFamily(
            "tapo_p100_today_runtime_mins",
            "Current running time for the TP-Link TAPO P110 Smart Socket today. (minutes)",
            labels=["ip_address", "room"],
        ),
        MetricType.MONTH_RUNTIME: GaugeMetricFamily(
            "tapo_p100_month_runtime_mins",
            "Current running time for the TP-Link TAPO P110 Smart Socket this month. (minutes)",
            labels=["ip_address", "room"],
        ),
        MetricType.TODAY_ENERGY: GaugeMetricFamily(
            "tapo_p100_today_energy_wh",
            "Energy consumed by the TP-Link TAPO P110 Smart Socket today. (Watt-hours)",
            labels=["ip_address", "room"],
        ),
        MetricType.MONTH_ENERGY: GaugeMetricFamily(
            "tapo_p100_month_energy_wh",
            "Energy consumed by the TP-Link TAPO P110 Smart Socket this month. (Watt-hours)",
            labels=["ip_address", "room"],
        ),
        MetricType.CURRENT_POWER: GaugeMetricFamily(
            "tapo_p100_power_consumption_w",
            "Current power consumption for TP-Link TAPO P110 Smart Socket. (Watts)",
            labels=["ip_address", "room"],
        ),
    }


RED_SUCCESS = "SUCCESS"
RED_FAILURE = "FAILURE"

@contextmanager
def time_observation(ip_address, room):
    caught = None
    status = RED_SUCCESS
    start = time()

    try:
        yield
    except Exception as e:
        status = RED_FAILURE
        caught = e
    
    duration = floor((time() - start) * 1000)
    OBSERVATION_RED_METRICS.labels(ip_address=ip_address, room=room, success=status).observe(duration)

    logger.debug("observation completed", extra={
        "ip": ip_address, "room": room, "duration_ms": duration,
    })

    if caught:
        raise caught


class Collector:
    def __init__(self, deviceMap, email_address, password):
        def create_device(ip_address, room):
            extra = {
                "ip": ip_address,
                "room": room,
            }
            logger.debug("connecting to device", extra=extra)
            
            exception_count = 0  # Counter for exceptions
            
            while True:
                try:
                    d = PyP100.P100(ip_address, email_address, password)
                    d.handshake()
                    d.login()
                except Exception as e:
                    exception_count += 1
                    logger.error("failed to connect to device", extra=extra, exc_info=True)
                    if exception_count >= 3:  # Return None after the third exception
                        d = None
                        break
                    sleep(1)  # Sleep for 1 second after each exception
                    continue
                break

            if d is not None:
                logger.debug("successfully authenticated with device", extra=extra)
            
            return d

        self.devices = {
            room: (ip_address, device)
            for room, ip_address in deviceMap.items()
            if (device := create_device(ip_address, room)) is not None
        }

    def get_device_data(self, device, ip_address, room):
        with time_observation(ip_address, room):
            logger.debug("retrieving energy usage statistics for device", extra={
                "ip": ip_address, "room": room,
            })
            return device.getEnergyUsage()

    def collect(self):
        logger.info("recieving prometheus metrics scrape: collecting observations")

        metrics = get_metrics()
        metrics[MetricType.DEVICE_COUNT].add_metric([], len(self.devices))

        for room, (ip_addr, device) in self.devices.items():
            logger.info("performing observations for device", extra={
                "ip": ip_addr, "room": room,
            })

            try:
              #  data = self.get_device_data(device, ip_addr, room)

                labels = [ip_addr, room]
              #  metrics[MetricType.TODAY_RUNTIME].add_metric(labels, data['today_runtime'])
              #  metrics[MetricType.MONTH_RUNTIME].add_metric(labels, data['month_runtime'])
              #  metrics[MetricType.TODAY_ENERGY].add_metric(labels, data['today_energy'])
              #  metrics[MetricType.MONTH_ENERGY].add_metric(labels, data['month_energy'])
              #  metrics[MetricType.CURRENT_POWER].add_metric(labels, data['current_power'])
            except Exception as e:
                logger.exception("encountered exception during observation!")

        for m in metrics.values():
            yield m        

            
