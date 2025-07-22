import time
import requests
from flask import Request, jsonify


APPSHEET_API_URL = "https://api.appsheet.com/api/v2/apps/ae1596bd-60af-4452-9e51-a42ee959d43a/tables/Project%20TS%20List/Action?applicationAccessKey=V2-dB3Wy-nJZXN-EH69R-habHQ-65ccB-W1rsL-JcTf3-2nylu"
APPSHEET_API_HEADERS = {
    "Content-Type": "application/json"
}

def measure_appsheet_api():
    # Measure start time
    start = time.time()
    try:
        # Dummy payload - adjust based on AppSheet needs
        payload = {
                "Action": "Find",
                "Properties": {
                "Locale": "en-US",
                "Location": "51.159133, 4.806236",
                "Timezone": "Central European Standard Time",
                "Selector": "Filter(Project TS List,[TS-ID]=202505INCSTAdde1fe60)",
                "UserSettings": {
                "Thisuseremail": "douae_ba@outlook.com"
                }
                },
                "Rows": [
                    {
                        "Reporting Month": "05/01/2025"
                    }
                ]
            }

        response = requests.post(APPSHEET_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        status = "success"
    except Exception as e:
        result = {"error": str(e)}
        status = "failed"

    duration = round(time.time() - start, 3)

    return duration, result, status
    
api_perf, result, status = measure_appsheet_api()
print("AppSheet API performance measurement= ", api_perf)
print("AppSheet API result= ", result)
