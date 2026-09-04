import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("INTERVALS_API_KEY")

# intervals.icu uses HTTP Basic Auth where the username is literally
# the string "API_KEY" and the password is your actual key.
# Testing against athlete "0" (a shortcut meaning "me") first, before
# touching any real activity data - cheapest possible way to confirm
# the auth mechanism actually works.
response = requests.get(
    "https://intervals.icu/api/v1/athlete/0",
    auth=("API_KEY", api_key),
)

activities_response = requests.get(
    "https://intervals.icu/api/v1/athlete/0/activities",
    params={"oldest": "2026-06-01", "newest": "2026-09-04"},
    auth=("API_KEY", api_key),
)

print("Status:", activities_response.status_code)
print(activities_response.json())