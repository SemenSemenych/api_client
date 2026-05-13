from api_client.client import GlobalPingClient, Location

def main():
    # Initialize the client (unauthenticated for this example)
    client = GlobalPingClient()

    print("Triggering measurement from Germany (DE)...")
    try:
        # Run a ping measurement targeting google.com from Germany
        # We use the Location class for structured targeting
        result = client.run_measurement(
            target="google.com",
            measurement_type="ping",
            locations=[Location(country="DE")]
        )

        print("\nMeasurement completed successfully!")
        print(f"Status: {result.get('status')}")
        print(f"Results count: {len(result.get('results', []))}")

        # Print first result if available
        if result.get('results'):
            first_res = result['results'][0]
            print(f"First probe location: {first_res.get('probe', {}).get('location')}")
            print(f"Response: {first_res.get('result')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
