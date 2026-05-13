import pytest
import respx
from httpx import Response

from api_client.client import GlobalPingClient, GlobalPingMeasurement


@respx.mock
def test_start_success():
    # Arrange
    client = GlobalPingClient()
    mock_response_data = {"id": "test-measurement-id-123"}
    respx.post(client.MEASUREMENT_URL).mock(
        return_value=Response(202, json=mock_response_data)
    )

    # Act
    client._start(
        measurement=GlobalPingMeasurement.PING,
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
    respx.post(client.MEASUREMENT_URL).mock(return_value=Response(400))

    # Act & Assert
    with pytest.raises(Exception):
        client._start(measurement=GlobalPingMeasurement.PING, target="8.8.8.8")
