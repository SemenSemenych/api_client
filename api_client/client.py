import time
from enum import StrEnum

import httpx

from .models import LimitsModel, CreateLimitsModel


class GlobalPingMeasurement(StrEnum):
    ping = "ping"
    traceroute = "traceroute"
    dns = "dns"
    mtr = "mtr"
    http = "http"


class GlobalPingClient:
    base_url = "https://api.globalping.io"
    measurement_url = "/v1/measurements"
    limits_url = "/v1/limits"

    def __init__(self):
        self.client = httpx.Client(base_url=self.base_url)
        self.limits = None
        self.request_result = None

    def acquire_limits(self) -> CreateLimitsModel | None:
        response = self.client.request("GET", self.limits_url)
        if response.is_success:
            limits_result = response.json()
            limits = LimitsModel(**limits_result)
            self.limits = limits.rateLimit.measurements.create
            return limits.rateLimit.measurements.create
        else:
            response.raise_for_status()
            return None

    def ping(
        self,
        target: str,
        location: str = "",
        retries: int = 5,
        interval: int = 5,
        **kwargs,
    ) -> None:
        self._start(GlobalPingMeasurement.ping, target, location, **kwargs)
        for _ in range(retries):
            self._get_result()
            if self.request_result and self.request_result.get("status") == "finished":
                return self.request_result.get("results", [{}])[0].get("result", {})
            time.sleep(interval)

        raise TimeoutError(f"Ping failed to finish after {retries} retries")

    def _start(
        self,
        measurement: GlobalPingMeasurement,
        target: str,
        location: str = "",
        **kwargs,
    ) -> None:
        response = self.client.request(
            "POST",
            self.measurement_url,
            json={
                "type": measurement.value,
                "target": target,
                "location": location,
                "measurementOptions": kwargs,
            },
        )

        if response.is_success:
            self.id = response.json()["id"]
        else:
            response.raise_for_status()

    def _get_result(self) -> None:
        if self.id:
            response = self.client.request("GET", f"{self.measurement_url}/{self.id}")
            if response.is_success:
                request_result = response.json()
                if request_result["status"] == "finished":
                    self.request_result = request_result
            else:
                response.raise_for_status()
