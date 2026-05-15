import httpx
import pytest
import respx

from api_client.client import GlobalPingClient, GlobalPingMeasurement
from api_client.models_limit import CreateLimitsModel
from api_client.models_ping import ResultPropsModel


@respx.mock
def test_start_success():
    # Arrange
    client = GlobalPingClient()
    mock_response_data = {
        "id": "PY5fMsREMmIq45VR",
        "probesCount": 1
    }
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
    assert client.id == "PY5fMsREMmIq45VR"
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
    answer_limits_dictionary = {"type": "ip", "limit": 100, "remaining": 95, "reset": 3599}
    mock_limits_data = {
        "rateLimit": {"measurements": {"create": answer_limits_dictionary}}}
    respx.get(f"{client.base_url}{client.limits_url}").mock(
        return_value=httpx.Response(httpx.codes.OK, json=mock_limits_data)
    )

    # Act
    limits_result = client.acquire_limits()

    # Assert
    assert limits_result == CreateLimitsModel(**answer_limits_dictionary)
    assert client.limits == CreateLimitsModel(**answer_limits_dictionary)
    assert len(respx.calls) == 1

def pending_dicts():
    client = GlobalPingClient()
    mock_start_data = {
        "id": "PY5fMsREMmIq45VR",
        "probesCount": 1
    }
    mock_result_pending = {
        "id": "PY5fMsREMmIq45VR",
        "type": "ping",
        "status": "pending",
        "createdAt": "2023-07-14T18:25:52.414Z",
        "updatedAt": "2023-07-14T18:25:53.207Z",
        "target": "cdn.jsdelivr.net",
        "probesCount": 1,
        "measurementOptions": {
            "packets": 2
        },
    }
    return client, mock_start_data, mock_result_pending

@respx.mock
def test_ping_success():
    # Arrange

    client, mock_start_data, mock_result_pending = pending_dicts()

    test_answer_dictionary = {"status": "finished",
                              "rawOutput": "PING jsdelivr.map.fastly.net (151.101.129.229) 56(84) bytes of data. 64 bytes from 151.101.129.229 (151.101.129.229): icmp_seq=1 ttl=59 time=24.2 ms 64 bytes from 151.101.129.229 (151.101.129.229): icmp_seq=2 ttl=59 time=24.2 ms --- jsdelivr.map.fastly.net ping statistics --- 2 packets transmitted, 2 received, 0% packet loss, time 201ms rtt min/avg/max/mdev = 24.174/24.183/24.193/0.009 ms",
                              "resolvedAddress": "151.101.129.229",
                              "resolvedHostname": "151.101.129.229",
                              "timings": [
                                  {
                                      "ttl": 59,
                                      "rtt": 24.2
                                  },
                                  {
                                      "ttl": 59,
                                      "rtt": 24.2
                                  }
                              ],
                              "stats": {
                                  "min": 24.174,
                                  "max": 24.193,
                                  "avg": 24.183,
                                  "total": 2,
                                  "loss": 0,
                                  "rcv": 2,
                                  "drop": 0
                              }}

    mock_result_finished = {
        "id": "nzGzfAGL7sZfUs3c",
        "type": "ping",
        "status": "finished",
        "createdAt": "2023-07-14T18:25:52.414Z",
        "updatedAt": "2023-07-14T18:25:53.207Z",
        "target": "cdn.jsdelivr.net",
        "probesCount": 1,
        "measurementOptions": {
            "packets": 2
        },
        "results": [
            {
                "probe": {
                    "continent": "OC",
                    "region": "Australia and New Zealand",
                    "country": "NZ",
                    "state": None,
                    "city": "Auckland",
                    "asn": 61138,
                    "longitude": 174.77,
                    "latitude": -36.87,
                    "network": "Zappie Host LLC",
                    "tags": [
                        "datacenter-network"
                    ],
                    "resolvers": [
                        "1.1.1.1",
                        "8.8.8.8"
                    ]
                },
                "result": test_answer_dictionary
            }
        ]
    }

    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.ACCEPTED, json=mock_start_data)
    )
    respx.get(f"{client.measurement_url}/PY5fMsREMmIq45VR").mock(
        side_effect=[
            httpx.Response(httpx.codes.OK, json=mock_result_pending),
            httpx.Response(httpx.codes.OK, json=mock_result_finished),
        ]
    )

    # Act
    ping_result = client.ping(target="8.8.8.8", interval=1)

    # Assert
    assert ping_result == ResultPropsModel(**test_answer_dictionary)
    assert len(respx.calls) == 3


@respx.mock
def test_ping_timeout():
    # Arrange
    client, mock_start_data, mock_result_pending = pending_dicts()

    respx.post(client.measurement_url).mock(
        return_value=httpx.Response(httpx.codes.ACCEPTED, json=mock_start_data)
    )
    respx.get(f"{client.measurement_url}/PY5fMsREMmIq45VR").mock(
        return_value=httpx.Response(httpx.codes.OK, json=mock_result_pending)
    )

    # Act & Assert
    with pytest.raises(TimeoutError) as excinfo:
        client.ping(target="8.8.8.8", retries=2, interval=1)

    assert "Ping failed to finish after 2 retries" in str(excinfo.value)
