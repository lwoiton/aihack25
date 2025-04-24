from dMB_client import DriveMyBoxClient, DriveMyBoxAPIException

def test_price_quotation():
    # Initialize client with test environment settings
    client = DriveMyBoxClient(
        api_key="kWLCfCNq7JaOKcoE5Kq8m7Mm8bp1gbMJ4ooDrG6Q",
        base_url="https://api.test.drivemybox.io/"  # Test environment
    )
    
    print("Preparing quotation request for the test environment...")
    
    # Create a quotation request following the structure in the API docs
    payload = {
		"route": {
			"route_loading_points": [
				{
					"address": {
					"discriminator": "ExtendedAddress",
					"city": "Musterstadt",
					"country": "Germany",
					"postal_code": "12345"
					# Simplified to reduce possible errors
					},
					"discriminator": "ExtendedRouteLoadingPointCreation",
					"sequence_number": 1,
					"type": "WAREHOUSE",
					"provision_location": True
				}
			]
		},
		"containers": [
			{
			"sequence_number": 1,
			"type_code": "22G1",
			"provision_at": "2025-05-01T12:30:25Z",  # Updated to future date
			"assumed_net_weight": 18000,
			"assumed_tara": 18000
			}
		]
	}
    
    try:
        print("Sending quotation request to the test API endpoint...")
        quotation_result = client.create_price_quotation(payload)
        
        # Process and display the response
        print("\nQuotation received successfully from the test environment!")
        
        # Extract route information
        route_info = quotation_result.get("route", {})
        print(f"\nRoute Information:")
        print(f"- Distance: {route_info.get('distance', 'N/A')} meters")
        print(f"- CO2 Emission: {route_info.get('co2_emission', 'N/A')} kg")
        
        # Extract price information
        prices = quotation_result.get("prices", [])
        if prices:
            for i, price_info in enumerate(prices):
                print(f"\nPrice Quote #{i+1}:")
                
                # Main price
                main_price = price_info.get("price", {})
                price_amount = main_price.get("amount", "N/A")
                price_currency = main_price.get("currency", "N/A")
                print(f"- Total Price: {price_amount} {price_currency}")
                
                # Pricing details
                print(f"- Pricing Mode: {price_info.get('pricing_mode', 'N/A')}")
                
                # Check if it's long haulage or round trip
                is_long_haulage = price_info.get("is_long_haulage", False)
                is_round_trip = price_info.get("is_round_trip", False)
                print(f"- Long Haulage: {'Yes' if is_long_haulage else 'No'}")
                print(f"- Round Trip: {'Yes' if is_round_trip else 'No'}")
                
                # Toll
                toll = price_info.get("toll", {})
                toll_amount = toll.get("amount", "N/A")
                toll_currency = toll.get("currency", "N/A")
                print(f"- Toll: {toll_amount} {toll_currency}")
                
                # Carbon offset
                carbon_offset = price_info.get("carbon_offset", {})
                if carbon_offset:
                    carbon_amount = carbon_offset.get("amount", "N/A")
                    carbon_currency = carbon_offset.get("currency", "N/A")
                    print(f"- Carbon Offset: {carbon_amount} {carbon_currency}")
                
                # Service prices
                services = price_info.get("container_services", [])
                if services:
                    print("- Added Services:")
                    for service in services:
                        service_type = service.get("service", {}).get("type", "N/A")
                        service_price = service.get("price", {})
                        service_amount = service_price.get("amount", "N/A")
                        service_currency = service_price.get("currency", "N/A")
                        print(f"  - {service_type}: {service_amount} {service_currency}")
                
                # Container-specific prices
                containers = price_info.get("containers", [])
                if containers:
                    print("- Container Prices:")
                    for container in containers:
                        seq_num = container.get("sequence_number", "N/A")
                        container_price = container.get("price", {})
                        container_amount = container_price.get("amount", "N/A")
                        container_currency = container_price.get("currency", "N/A")
                        print(f"  - Container #{seq_num}: {container_amount} {container_currency}")
        else:
            print("No price information received.")
        
    except DriveMyBoxAPIException as e:
        print(f"\nAPI Error: {e}")
        if hasattr(e, 'details') and e.details:
            print(f"Error details: {e.details}")
            
            # Provide more help for common API errors
            if e.status_code == 401:
                print("\nThis appears to be an authentication error. Please check that:")
                print("1. The API key is correct")
                print("2. The API key has permission to access the test environment")
                print("3. The base URL is correct for the test environment")
            elif e.status_code == 400:
                print("\nThis appears to be a bad request error. The API rejected the data format.")
                print("Common issues include:")
                print("1. Missing required fields in the request")
                print("2. Invalid values for fields (e.g., wrong container type code)")
                print("3. Incorrect data types (e.g., string instead of number)")
                
    except ValueError as e:
        print(f"\nValidation Error: {e}")
        print("\nThe client's validation caught an issue before sending the request.")
        print("This is helpful as it saves an API call and gives you immediate feedback.")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nThis is an unhandled exception that wasn't expected by the client.")
        print("It might indicate a bug in the client or an unusual response from the API.")

if __name__ == "__main__":
    test_price_quotation()