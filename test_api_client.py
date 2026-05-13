from turtle import ht

import httpx
import pytest
import respx

from api_client.client import GlobalPingClient, GlobalPingMeasurement


@respx.mock
def test_start_success():
    # Arrange
    client = GlobalPingClient()
    mock_response_data = {"id": "test-measurement-id-123"}
    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.ACCEPTED, json=mock_response_data)
    )

    # Act
    client._start(
        measurement=GlobalPingMeasurement.ping,
        target="8.8.8.8",
        location="US",
        custom_option="value",
    )

    # Assert
    assert client.id == "test-measurement-id-123"
    request = respx.calls.last
    json_data = request.request.content.decode()
    assert "ping" in json_data
    assert "8.8.8.8" in json_data
    assert "US" in json_data
    assert "custom_option" in json_data


@respx.mock
def test_start_failure():
    # Arrange
    client = GlobalPingClient()
    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.BAD_REQUEST)
    )

    # Act & Assert
    with pytest.raises(Exception):
        client._start(measurement=GlobalPingMeasurement.ping, target="8.8.8.8")


@respx.mock
def test_limits_success():
    # Arrange
    client = GlobalPingClient()
    mock_limits_data = {"rateLimit": {"measurements": {"limit": 100, "remaining": 50}}}
    respx.get(f"{client.base_url}{client.limits_url}").mock(
        return_value=httpx.Response(httpx.codes.OK, json=mock_limits_data)
    )

    # Act
    limits_result = client.acquire_limits()

    # Assert
    assert limits_result == {"limit": 100, "remaining": 50}
    assert client.limits == {"limit": 100, "remaining": 50}
    assert len(respx.calls) == 1


@respx.mock
def test_ping_success():
    # Arrange
    client = GlobalPingClient()
    mock_start_data = {"id": "test-ping-id"}
    mock_result_pending = {"status": "pending"}
    mock_result_finished = {
        "status": "finished",
        "results": [{"result": {"latency": 10, "loss": 0}}],
    }

    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.ACCEPTED, json=mock_start_data)
    )
    respx.get(f"{client.measurement_url}/test-ping-id").mock(
        side_effect=[
            httpx.Response(httpx.codes.OK, json=mock_result_pending),
            httpx.Response(httpx.codes.OK, json=mock_result_finished),
        ]
    )

    # Act
    ping_result = client.ping(target="8.8.8.8", interval=1)

    # Assert
    assert ping_result == {"latency": 10, "loss": 0}
    assert len(respx.calls) == 3


@respx.mock
def test_ping_timeout():
    # Arrange
    client = GlobalPingClient()
    mock_start_data = {"id": "test-ping-timeout-id"}
    mock_result_pending = {"status": "pending"}

    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.ACCEPTED, json=mock_start_data)
    )
    respx.get(f"{client.measurement_url}/test-ping-timeout-id").mock(
        return_value=httpx.Response(httpx.codes.OK, json=mock_result_pending)
    )

    # Act & Assert
    with pytest.raises(TimeoutError) as excinfo:
        client.ping(target="8.8.8.8", retries=2, interval=1)

    assert "Ping failed to finish after 2 retries" in str(excinfo.value)
