# Importing the required libraries
import requests
import json
import os

# Defining the API endpoint URL
HEPAI_API_KEY = os.environ.get("HEPAI_API_KEY")
model = "R1_test"
function = "get_info"
url = f"https://aiapi.ihep.ac.cn/apiv2/worker/unified_gate/?model={model}&function={function}"

# post parameters
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {HEPAI_API_KEY}"
    }

# sending post request and saving response as response object
response = requests.post(url, headers=header, json={})

# extracting response text
print(response.text)