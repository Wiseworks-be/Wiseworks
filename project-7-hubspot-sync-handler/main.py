# MAIN.PY
# ************************************************************************************************
# THIS FLOW HANDLES SYNCHRONISATION OF DATA FROM HUBSPOT TO APPSHEET                            *
#                                                                                               *
# params: no params                                                                             *
#                                                                                               *
# creteated by: Marc De Krock                                                                   *
# date: 20250604                                                                                *
# last updated: 20250625                                                                        *
# last updated by: Marc De Krock                                                                *
# version: 1.0.0                                                                                *
# supports:  supports: contacts, companies, trainers, trainings, training session               *
# ************************************************************************************************


import os
from datetime import datetime, timezone
from webhook_utils_1 import send_push_notification, post_data_to_appsheet
from hubspot_utils import get_rows_from_json
from secret_manager_utils import get_secret
import logging

# from secret_manager_utils import get_secret
import uuid
import functions_framework
from flask import jsonify
from pathlib import Path
import json

# import logging
import google.auth


# Constants
# TW_app_id = "d243ce5a-5839-4f90-85e2-a17d064cc566"
# TW_app_access_key = "V2-XezCn-W5Ou9-KCPnm-27vab-kZQQw-4Z42a-cDmGn-qWrfC"
# app_name = "TrainWise-346984636"
# secret_value="7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d901fa57c3de8196a54be1f9a84cb29c07915320c6de5f13e98b94298c83e374bcbb6a"
# secret_value = "7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d90"


# ************** HERE IT STARTS ***********************
# **SECRETS**
_, project_id = google.auth.default()
print("Project ID: ", project_id)
"""PROJECT_ID = project_id
SECRET_ID = "Appkey_A1"

secret_value = get_secret(SECRET_ID, PROJECT_ID)

print("****************My secret value:", secret_value)"""

# **GET BASEPATH
base_path = Path(os.getcwd())
print("Working directory:", os.getcwd())

# base_path = Path(__file__).parent
logging.basicConfig(level=logging.DEBUG)
project_id = "my-project-trial-1-441910"


secret_value = get_secret(secret_id="AppKey", project_id=project_id)
print("****************My secret value:", secret_value)
TW_app_id = get_secret(secret_id="TW_app_id", project_id=project_id)
print("****************My TW_app_id:", TW_app_id)
TW_app_access_key = get_secret(secret_id="TW_app_access_key", project_id=project_id)
print("****************My TW_app_access_key:", TW_app_access_key)
app_name = get_secret(secret_id="TW_app_name", project_id=project_id)
print("****************My TW_app_name:", app_name)

print("OK, all secrets loaded successfully")
print("NOW WAITING FOR A WEBHOOK CALL FROM HUBSPOT...")


@functions_framework.http
def main(request):
    # ************** HERE IT STARTS ***********************
    # **SECRETS**
    _, project_id = google.auth.default()
    print("Project ID: ", project_id)
    """PROJECT_ID = project_id
    SECRET_ID = "Appkey_A1"

    secret_value = get_secret(SECRET_ID, PROJECT_ID)

    print("****************My secret value:", secret_value)"""

    # **GET BASEPATH
    base_path = Path(os.getcwd())
    print("Working directory:", os.getcwd())

    # base_path = Path(__file__).parent
    # TESTRUN
    test_run = request.args.get("test")
    if test_run:
        print("Test run, skipping security checks and processing")
        return jsonify({"message": "Test run, no processing done"}), 200
    # SECURITY CHECK
    # incoming_key = request.headers.get("AppKey")
    incoming_key = request.args.get(
        "AppKey"
    )  # in case of Trainwise webhook from hubspot
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
        entry_timestamp = datetime.now(timezone.utc).isoformat()
        random_uuid = str(uuid.uuid4())
        print("json data from hubspot", json.dumps(json_data, indent=2))
        print("______________________________________________")
        # SHOW timestamp and UUID, add later to the XML
        print("timestamp: ", entry_timestamp)
        print("random_uuid: ", random_uuid)
        print("______________________________________________")
        # **************************************************
        # PROCESS THE JSON DATA
        # **************************************************

        (
            mapped_records,
            object_type,
            table_name,
            change_flag,
            is_creation_event,
            is_deletion_event,
            is_creation_or_update_event,
        ) = get_rows_from_json(json_data)
        print("*******************************************")
        print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
        print("Object type:", object_type)
        print("Table name:", table_name)
        print("Change flag:", change_flag)
        print("Is creation event:", is_creation_event)
        print("Is deletion event:", is_deletion_event)
        print("Is creation or update event:", is_creation_or_update_event)
        print("*******************************************")
        add_or_update_rows = (
            mapped_records[0] if mapped_records else None
        )  # Get the first record from the list
        print(
            "Rows to be posted to AppSheet:", json.dumps(add_or_update_rows, indent=2)
        )
        print("json_data:", json.dumps(json_data, indent=2))
        # in the training sessions table the start_date and end_date is a timestamp in milliseconds
        # Convert start_date from string to int, then to ISO format
        if table_name == "training_sessions" and not change_flag in ["DELETED"]:
            # Process the training_sessions table
            print("Processing training_sessions table")
            if "start_date" in add_or_update_rows:
                start_date = add_or_update_rows["start_date"]
                if isinstance(start_date, str):
                    start_date = int(start_date)
                add_or_update_rows["start_date"] = datetime.fromtimestamp(
                    start_date / 1000, timezone.utc
                ).isoformat()
            if "end_date" in add_or_update_rows:
                end_date = add_or_update_rows["end_date"]
                if isinstance(end_date, str):
                    end_date = int(end_date)
                add_or_update_rows["end_date"] = datetime.fromtimestamp(
                    end_date / 1000, timezone.utc
                ).isoformat()
            print(
                "ROWS AFTER PROCESSING training_sessions:",
                json.dumps(add_or_update_rows, indent=2),
            )

        if (
            change_flag == "CREATED" and not add_or_update_rows
        ):  # change_flag but rows is empty something went wrong
            print("No rows found in the mapped records")
            return jsonify({"error": "No rows found in the mapped records"}), 400
        print(
            "Rows to be posted to AppSheet:", json.dumps(add_or_update_rows, indent=2)
        )
        # **************************************************
    except Exception as e:
        print("Error processing JSON data:", str(e))
        return jsonify({"error": f"Failed to process JSON data: {str(e)}"}), 500
    # **************************************************
    # IF CREATED POST TO APPSHEET
    # **************************************************
    if is_creation_event and change_flag == "CREATED":
        print("@@@@ This is a creation event, we will create a new record in AppSheet")
        # POST DATA TO APPSHEET
        try:
            print("Posting data to AppSheet...")
            # selector = "Filter(invoices,[Customer]= 34f09c29)"  # Example selector, adjust as needed
            # user_settings = {"User role": "Super Administrator"}  # Example user setting
            # post_data_to_appsheet(table, rows=None, action=None, selector=None, app_name=None, app_id=None, app_access_key=None):
            add_rows_bracketed = [add_or_update_rows]
            response = post_data_to_appsheet(
                table=table_name,
                rows=add_rows_bracketed,
                action="Add",
                selector=None,
                user_settings=None,
                app_name=app_name,
                app_id=TW_app_id,
                app_access_key=TW_app_access_key,
            )
            print(
                "Response from AppSheet:", response.status_code, "BODY: ", response.text
            )
            if response.status_code != 200:
                return (
                    jsonify({"error": "Failed to post data to AppSheet"}),
                    response.status_code,
                )
            if not response.text:
                return (
                    jsonify(
                        {
                            "error": f"Failed to post data to AppSheet, table or record not found: {response.text}"
                        }
                    ),
                    response.status_code,
                )
            # response = post_data_to_appsheet_whc(mapped_record, app_name, WHC_app_id, WHC_app_access_key)
            # print("Response from AppSheet:", response)
        except Exception as e:
            return jsonify({"error": f"Failed to post data to AppSheet: {str(e)}"}), 500
    # **************************************************
    # IF ONE OR MORE RECORDS DELETED POST TO APPSHEET
    # **************************************************
    elif is_deletion_event and change_flag == "DELETED":
        for event in json_data:
            object_id = event["objectId"]
            if table_name == "companies":
                selector = f"Filter(companies,[hs_company_id]={object_id})"
            elif table_name == "contacts":
                selector = f"Filter(contacts,[hs_contact_id]={object_id})"
            elif table_name == "trainers":
                selector = f"Filter(trainers,[hs_trainer_id]={object_id})"
            elif table_name == "trainings":
                selector = f"Filter(trainings,[hs_training_id]={object_id})"
            elif table_name == "training_sessions":
                selector = (
                    f"Filter(training_sessions,[hs_training_session_id]={object_id})"
                )
            else:
                print(f"⚠️ No selector logic for table: {table_name}")
                continue
            # Now you can make your AppSheet API DELETE call here
            # **************************************************
            # FIND THE RECORDS TO DELETE IN APPSHEET
            # **************************************************
            print(f"Deleting from table '{table_name}' using selector: {selector}")
            try:
                response = post_data_to_appsheet(
                    table=table_name,
                    rows=None,
                    action="Find",
                    selector=selector,
                    user_settings=None,
                    app_name=app_name,
                    app_id=TW_app_id,
                    app_access_key=TW_app_access_key,
                )
                print(
                    "Response from AppSheet:",
                    response.status_code,
                    "BODY: ",
                    response.text,
                )
                if response.status_code != 200:
                    return (
                        jsonify({"error": "Failed to post data to AppSheet"}),
                        response.status_code,
                    )
                if not response.text:
                    return (
                        jsonify(
                            {
                                "error": f"Failed to post data to AppSheet, table or record not found: {response.text}"
                            }
                        ),
                        response.status_code,
                    )
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to post data to AppSheet: {str(e)}"}),
                    500,
                )
            try:
                # **************************************************
                # ACTUALLY DELETE THE RECORDS IN APPSHEET
                # **************************************************
                response_json = json.loads(response.text)
                if table_name == "contacts":
                    record_ids = [item["contact_id"] for item in response_json]
                elif table_name == "companies":
                    record_ids = [item["company_id"] for item in response_json]
                elif table_name == "trainers":
                    record_ids = [item["trainer_id"] for item in response_json]
                elif table_name == "trainings":
                    record_ids = [item["training_id"] for item in response_json]
                elif table_name == "training_sessions":
                    record_ids = [item["training_session_id"] for item in response_json]
                else:
                    print(f"⚠️ No record_id logic for table: {table_name}")
                    return (
                        jsonify(
                            {"error": f"No record_id logic for table: {table_name}"}
                        ),
                        400,
                    )
                print(
                    "the found contact_id's are: ",
                    record_ids,
                    " for table : ",
                    table_name,
                )

                for record_id in record_ids:
                    print(f"Deleting contact with ID: {record_id}")
                    if table_name == "contacts":
                        delete_rows = [{"contact_id": record_id}]
                    elif table_name == "companies":
                        delete_rows = [{"company_id": record_id}]
                    elif table_name == "trainers":
                        delete_rows = [{"trainer_id": record_id}]
                    elif table_name == "trainings":
                        delete_rows = [{"training_id": record_id}]
                    elif table_name == "training_sessions":
                        delete_rows = [{"training_session_id": record_id}]
                    else:
                        print(f"⚠️ No rows logic for table: {table_name}")
                        return (
                            jsonify(
                                {"error": f"No rows logic for table: {table_name}"}
                            ),
                            400,
                        )
                    print("rows to delete: ", delete_rows)
                    # delete_response = post_data_to_appsheet(table="contacts", rows=None, action="Delete", selector=f"Filter(contacts,[contact_id]= {contact_id})", user_settings=None, app_name=app_name, app_id=TW_app_id, app_access_key=TW_app_access_key)
                    delete_response = post_data_to_appsheet(
                        table=table_name,
                        rows=delete_rows,
                        action="Delete",
                        selector=None,
                        user_settings=None,
                        app_name=app_name,
                        app_id=TW_app_id,
                        app_access_key=TW_app_access_key,
                    )
                    print(
                        "Delete Response from AppSheet:",
                        delete_response.status_code,
                        "BODY: ",
                        delete_response.text,
                    )
                    if delete_response.status_code != 200:
                        return (
                            jsonify({"error": "Failed to delete data from AppSheet"}),
                            delete_response.status_code,
                        )
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to post data to AppSheet: {str(e)}"}),
                    500,
                )
    # **************************************************
    # THIS IS THE UPDATE SECTION
    # **************************************************
    elif (
        is_creation_or_update_event and not change_flag
    ):  # change_flag is None or empty so no DELETED or CREATED
        print(
            "@@@ This is a property change event, we will update the record in AppSheet"
        )
        to_update_object_id = next(
            (item.get("objectId") for item in json_data if "objectId" in item), None
        )
        print("table_name: ", table_name)
        # POST DATA TO APPSHEET
        try:
            print(
                "Posting data to AppSheet for update first do a find to see if the record already exist..."
            )

            print("object id to UPDATE: ", to_update_object_id)
            if not to_update_object_id:
                return jsonify({"error": "Object ID not found in the JSON data"}), 400
            if table_name == "companies":
                add_or_update_selector = (
                    f"Filter(companies,[hs_company_id]={to_update_object_id})"
                )
            elif table_name == "contacts":
                add_or_update_selector = (
                    f"Filter(contacts,[hs_contact_id]={to_update_object_id})"
                )
            elif table_name == "trainers":
                add_or_update_selector = (
                    f"Filter(trainers,[hs_trainer_id]={to_update_object_id})"
                )
            elif table_name == "trainings":
                add_or_update_selector = (
                    f"Filter(trainings,[hs_training_id]={to_update_object_id})"
                )
            elif table_name == "training_sessions":
                add_or_update_selector = f"Filter(training_sessions,[hs_training_session_id]={to_update_object_id})"
            else:
                print(f"⚠️ No selector logic for table: {table_name}")

            print("selector: ", add_or_update_selector)
            response = post_data_to_appsheet(
                table=table_name,
                rows=None,
                action="Find",
                selector=add_or_update_selector,
                user_settings=None,
                app_name=app_name,
                app_id=TW_app_id,
                app_access_key=TW_app_access_key,
            )
            print(
                "Response from AppSheet:", response.status_code, "BODY: ", response.text
            )
            json_data_from_appsheet = json.loads(response.text)
            print(
                "json_data_from_appsheet: ",
                json.dumps(json_data_from_appsheet, indent=2),
            )
            if response.status_code != 200:
                return (
                    jsonify({"error": "Failed to post data to AppSheet"}),
                    response.status_code,
                )
            if (
                not json_data_from_appsheet
            ):  # response is empty, so we will create a new record
                print(
                    "response from AppSheet is empty, no record found, so, creating a new record instead"
                )
                response = post_data_to_appsheet(
                    table=table_name,
                    rows=[add_or_update_rows],
                    action="Add",
                    selector=None,
                    user_settings=None,
                    app_name=app_name,
                    app_id=TW_app_id,
                    app_access_key=TW_app_access_key,
                )
                print(
                    "Response from AppSheet:",
                    response.status_code,
                    "BODY: ",
                    response.text,
                )
                if response.status_code != 200:
                    return (
                        jsonify({"error": "Failed to post data to AppSheet"}),
                        response.status_code,
                    )
                if not response.text:
                    return (
                        jsonify(
                            {
                                "error": f"Failed to post data to AppSheet, table or record could not be created: {response.text}"
                            }
                        ),
                        response.status_code,
                    )
            else:  # the record is already there, so we will update it now
                try:
                    print("UPDATING data to AppSheet...")
                    table_key_mapping = {
                        "contacts": "contact_id",
                        "companies": "company_id",
                        "trainings": "training_id",
                        "trainers": "trainer_id",
                        "training_sessions": "training_session_id",
                    }
                    # selector = "Filter(invoices,[Customer]= 34f09c29)"  # Example selector, adjust as needed
                    # user_settings = {"User role": "Super Administrator"}  # Example user setting
                    # post_data_to_appsheet(table, rows=None, action=None, selector=None, app_name=None, app_id=None, app_access_key=None):
                    key_column = table_key_mapping.get(table_name)

                    if not key_column:
                        raise ValueError(
                            f"❌ No key column mapping for table '{table_name}'"
                        )

                    # Extract the record_id from the AppSheet response
                    record_id_for_update = json_data_from_appsheet[0][key_column]
                    print("record_id_for_update:", record_id_for_update)

                    # Construct the update row with dynamic key column
                    add_or_update_rows = [
                        {
                            key_column: record_id_for_update,
                            **add_or_update_rows,  # this must be a dict, not a list
                        }
                    ]
                    # Print final payload
                    print(
                        "Rows to be posted to AppSheet for update:",
                        json.dumps(add_or_update_rows, indent=2),
                    )
                    print(
                        "Rows to be posted to AppSheet for update:",
                        json.dumps(add_or_update_rows, indent=2),
                    )
                    response = post_data_to_appsheet(
                        table=table_name,
                        rows=add_or_update_rows,
                        action="Edit",
                        selector=None,
                        user_settings=None,
                        app_name=app_name,
                        app_id=TW_app_id,
                        app_access_key=TW_app_access_key,
                    )
                    print(
                        "Response from AppSheet:",
                        response.status_code,
                        "BODY: ",
                        response.text,
                    )
                    if response.status_code != 200:
                        return (
                            jsonify({"error": "Failed to post data to AppSheet"}),
                            response.status_code,
                        )
                    if not response.text:
                        return (
                            jsonify(
                                {
                                    "error": f"Failed to post data to AppSheet, table or record not found: {response.text}"
                                }
                            ),
                            response.status_code,
                        )
                except Exception as e:
                    return (
                        jsonify(
                            {"error": f"Failed to post data to AppSheet: {str(e)}"}
                        ),
                        500,
                    )

        except Exception as e:
            return jsonify({"error": f"Failed to post data to AppSheet: {str(e)}"}), 500
    else:
        print(
            "This is not a creation event nor a deletion, nor a update, so we will not do anything"
        )

    return (
        jsonify(
            {"project_id": project_id, "message": "the Appsheet table has been updated"}
        ),
        200,
    )
