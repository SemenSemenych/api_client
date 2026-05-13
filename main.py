from api_client.client import GlobalPingClient, GlobalPingMeasurement
from storage.logic import Storage


class TestData:
    def __init__(self, storage: Storage, api_client: GlobalPingClient):
        self.storage = storage
        self.api_client = api_client


def main():
    storage = Storage()
    api_client = GlobalPingClient()
    test_data = TestData(storage, api_client)
    print("Modules imported.")


if __name__ == "__main__":
    main()
