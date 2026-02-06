from django.test import TestCase

# Create your tests here.


from kotak_integration_standalone import KotakNeoAPI

# Initialize API
api = KotakNeoAPI(user_id='client26349')

# Get positions (returns mock data)
positions = api.get_positions()
print(f"Positions: {positions}")

# Get holdings (returns mock data)
holdings = api.get_holdings()
print(f"Holdings: {holdings}")
