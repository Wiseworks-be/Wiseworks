
# MAIN.PY
#************************************************************************************************
# THIS FLOW HAS MULTIPLE FUNCTIONS TO SUPPORT OTHER API CALLS.                                  *
#                                                                                               *
# params: delay=1,2,3... (seconds)                                                              *
#         test=1 (test run, no processing done, optional)                                       *
#         AppKey=7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d90 (secret key)    *
#                                                                                               *
# creteated by: Marc De Krock                                                                   *
# date: 20250627                                                                                *
# last updated: 20250627                                                                        *
# last updated by: Marc De Krock                                                                *
# version: 1.0.0                                                                                *
# Initial version                                                                               *
#************************************************************************************************



import functions_framework
from flask import jsonify
import google.auth
import time

secret_value="7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d90"

@functions_framework.http
def main(request):
    # ************** HERE IT STARTS ***********************
    #**SECRETS**
    _, project_id = google.auth.default()
    print("Project ID: ", project_id)
    #TESTRUN
    test_run=request.args.get('test')
    if test_run:
        print("Test run, skipping security checks and processing")
        return jsonify({"message": "Test run, no processing done"}), 200
    # SECURITY CHECK
    #incoming_key = request.headers.get("AppKey")
    incoming_key = request.args.get("AppKey") #in case of Trainwise webhook from hubspot
    print("***Incoming key: ", incoming_key)
    print("***Secret value: ", secret_value)
    if incoming_key != secret_value:
        print("Invalid key")
        return jsonify({"error": "Invalid key"}), 403
    print("Valid key")
    # END SECURITY CHECK

    # GET THE JSON BODY
    if request.method != "POST":
        return jsonify({"error": "Only POST requests are allowed, you stupid 😁"}), 405
    try:
        json_data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
        
    try:
        delay = int(request.args.get("delay", 0))
    except ValueError:
        delay = 0

    if delay > 0:
        if delay > 20:
            delay = 20
        print(f"Delaying response by {delay} seconds, cannot be more than 20 seconds")
        time.sleep(delay)

    return jsonify({
        "message": f"Response delayed by {delay} seconds"
    })
