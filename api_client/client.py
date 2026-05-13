from enum import StrEnum

import httpx


class GlobalPingMeasurement(StrEnum):
    PING = "ping"
    TRACEROUTE = "traceroute"
    DNS = "dns"
    MTR = "mtr"
    HTTP = "http"


class GlobalPingClient:
    BASE_URL = "https://api.globalping.io"
    MEASUREMENT_URL = "/v1/measurements"

    def __init__(self):
        self.client = httpx.Client(base_url=self.BASE_URL)

    def _start(
        self,
        measurement: GlobalPingMeasurement,
        target: str,
        location: str = "",
        **kwargs,
    ) -> None:
        response = self.client.request(
            "POST",
            self.MEASUREMENT_URL,
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
            response = self.client.request("GET", f"{self.MEASUREMENT_URL}/{self.id}")
            if response.is_success:
                result = response.json()
                if result["status"] == "finished":
                    self.result = result
            else:
                response.raise_for_status()
