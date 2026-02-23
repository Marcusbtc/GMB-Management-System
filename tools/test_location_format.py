"""
Quick test to see what format location names are in from the API
"""
# The location name from mybusinessbusinessinformation v1 is in format:
# "locations/{locationId}"

# But mybusiness v4 requires:
# "accounts/{accountId}/locations/{locationId}"

# So we need to construct the full path when calling v4 APIs

example_location = "locations/9517224025366036950"
example_account = "accounts/123456789"

# To construct the full path:
full_path = f"{example_account}/{example_location}"
print(f"Full path: {full_path}")
# Result: accounts/123456789/locations/9517224025366036950
