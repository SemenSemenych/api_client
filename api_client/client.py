import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import requests


@dataclass
class Location:
    """
    Defines the location from which to run the measurement.
    """

    magic: Optional[str] = None
    country: Optional[str] = None
    limit: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class GlobalPingClient:
    """
    A client for the GlobalPing REST API.
    """

    BASE_URL = "https://api.globalping.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GlobalPing client.

        :param api_key: Your GlobalPing API key. If None, requests will be unauthenticated.
        """
        self.api_key = api_key
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, json=data, params=params)
        response.raise_for_status()
        return response.json()

    def create_measurement(
        self,
        target: str,
        measurement_type: str,
        locations: List[Union[Location, Dict]],
        options: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Trigger a new network measurement.

        :param target: The target hostname or IP.
        :param measurement_type: Type of test ('ping', 'dns', 'traceroute', 'mtr', 'http').
        :param locations: List of location objects or dicts.
        :param options: Optional measurement options.
        :return: The API response containing the measurement ID.
        """
        processed_locations = [
            loc.to_dict() if isinstance(loc, Location) else loc for loc in locations
        ]

        payload = {
            "target": target,
            "type": measurement_type,
            "locations": processed_locations,
        }
        if options:
            payload["measurementOptions"] = options

        return self._request("POST", "/measurements", data=payload)

    def get_measurement(self, measurement_id: str) -> Dict[str, Any]:
        """
        Retrieve the status and results of a specific measurement.

        :param measurement_id: The ID of the measurement.
        :return: The API response.
        """
        return self._request("GET", f"/measurements/{measurement_id}")

    def get_probes(self) -> Dict[str, Any]:
        """
        Get a list of all online probes.
        """
        return self._request("GET", "/probes")

    def get_limits(self) -> Dict[str, Any]:
        """
        Get current rate limits for the account/IP.
        """
        return self._request("GET", "/limits")

    def run_measurement(
        self,
        target: str,
        measurement_type: str,
        locations: List[Union[Location, Dict]],
        options: Optional[Dict] = None,
        poll_interval: float = 2.0,
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        """
        A synchronous wrapper that triggers a measurement and polls until it's finished.

        :param target: The target hostname or IP.
        :param measurement_type: Type of test.
        :param locations: List of location objects or dicts.
        :param options: Optional measurement options.
        :param poll_interval: Time to wait between polls (seconds).
        :param timeout: Total timeout for polling (seconds).
        :return: The final measurement result.
        """
        measurement = self.create_measurement(
            target, measurement_type, locations, options
        )
        m_id = measurement.get("id")
        if not m_id:
            raise ValueError("Failed to retrieve measurement ID from API response.")

        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Measurement {m_id} timed out after {timeout} seconds."
                )

            result = self.get_measurement(m_id)
            status = result.get("status")

            if status != "in-progress":
                return result

            time.sleep(poll_interval)
