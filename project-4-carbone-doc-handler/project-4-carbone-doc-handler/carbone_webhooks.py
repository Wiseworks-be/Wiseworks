import requests
import json
from flask import jsonify


#json_payload_local = "{'TS-ID': '202507TSTSTAb211053c', 'BU_Header_Logo': '', 'Business_Unit': 'Test BU', 'Consultant': 'TESTDUM1 TESTDUM1', 'Reporting_month_new': 'Jul-2025', 'Customer_name': 'New test client', 'Total_nr_hours_this_period': '72.00', 'Total_nr_days_this_period': '9.00', 'Nr_days_normal_this_period': '8.00', 'Nr_days_OT1_this_period': '0.50', 'Nr_days_OT2_this_period': '0.50', 'Cost_NMT_Act': '€250.00', 'Related_Project_TS_Calendars': [{'Project_TS_Calendar_ID': 'e0a835e5', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-01', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': 'c3b69f0f', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-02', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': 'c9c1580f', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-03', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '7f19415d', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-04', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '9ede8bfa', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-05', 'Nr_hours_normal': 0.0, 'Nr_hours_OT1': 4.0, 'Nr_hours_OT2': None, 'Comment': 'Zaterdag', 'Update': None, 'Last_change': '2025-07-10T09:02:05', 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 4.0, 'Nr_days_total': 0.5}, {'Project_TS_Calendar_ID': '107c3979', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-06', 'Nr_hours_normal': 0.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': 4.0, 'Comment': 'Zondag', 'Update': None, 'Last_change': '2025-07-10T09:02:29', 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 4.0, 'Nr_days_total': 0.5}, {'Project_TS_Calendar_ID': 'dffbdfcc', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-07', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '70b11165', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-08', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '30575f1e', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-09', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '2777ba0e', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-10', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}], 'Related_exception_times': [{'Exception_time_id': '02eb9c02', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': 'fb6ceb72', 'Quantity': 5.0, 'Note': '22 juli', 'Update': None, 'last_change': '2025-07-10T09:18:57', 'changed_by': 'nico.marien@sisusync.app'}, {'Exception_time_id': '4c5dffbe', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': '0dabfcf2', 'Quantity': 1.0, 'Note': '23 juli', 'Update': None, 'last_change': '2025-07-10T09:20:37', 'changed_by': 'nico.marien@sisusync.app'}, {'Exception_time_id': 'e54b603d', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': 'fb6ceb72', 'Quantity': 5.0, 'Note': '21/07/2025', 'Update': None, 'last_change': '2025-07-09T17:05:52', 'changed_by': 'nico.marien@sisusync.app'}]}"
# #****************************************************************
def call_carbone_render(template_id, access_token, json_payload):
    json_payload_local = "{'TS-ID': '202507TSTSTAb211053c', 'BU_Header_Logo': '', 'Business_Unit': 'Test BU', 'Consultant': 'TESTDUM1 TESTDUM1', 'Reporting_month_new': 'Jul-2025', 'Customer_name': 'New test client', 'Total_nr_hours_this_period': '72.00', 'Total_nr_days_this_period': '9.00', 'Nr_days_normal_this_period': '8.00', 'Nr_days_OT1_this_period': '0.50', 'Nr_days_OT2_this_period': '0.50', 'Cost_NMT_Act': '€250.00', 'Related_Project_TS_Calendars': [{'Project_TS_Calendar_ID': 'e0a835e5', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-01', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': 'c3b69f0f', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-02', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': 'c9c1580f', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-03', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '7f19415d', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-04', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '9ede8bfa', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-05', 'Nr_hours_normal': 0.0, 'Nr_hours_OT1': 4.0, 'Nr_hours_OT2': None, 'Comment': 'Zaterdag', 'Update': None, 'Last_change': '2025-07-10T09:02:05', 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 4.0, 'Nr_days_total': 0.5}, {'Project_TS_Calendar_ID': '107c3979', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-06', 'Nr_hours_normal': 0.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': 4.0, 'Comment': 'Zondag', 'Update': None, 'Last_change': '2025-07-10T09:02:29', 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 4.0, 'Nr_days_total': 0.5}, {'Project_TS_Calendar_ID': 'dffbdfcc', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-07', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '70b11165', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-08', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '30575f1e', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-09', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}, {'Project_TS_Calendar_ID': '2777ba0e', 'Project_TS_ID': '202507TSTSTAb211053c', 'Date': '2025-07-10', 'Nr_hours_normal': 8.0, 'Nr_hours_OT1': None, 'Nr_hours_OT2': None, 'Comment': None, 'Update': None, 'Last_change': None, 'Changed_by': 'nico.marien@sisusync.app', 'ProjectTSEmail': None, 'Nr_hours_total': 8.0, 'Nr_days_total': 1.0}], 'Related_exception_times': [{'Exception_time_id': '02eb9c02', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': 'fb6ceb72', 'Quantity': 5.0, 'Note': '22 juli', 'Update': None, 'last_change': '2025-07-10T09:18:57', 'changed_by': 'nico.marien@sisusync.app'}, {'Exception_time_id': '4c5dffbe', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': '0dabfcf2', 'Quantity': 1.0, 'Note': '23 juli', 'Update': None, 'last_change': '2025-07-10T09:20:37', 'changed_by': 'nico.marien@sisusync.app'}, {'Exception_time_id': 'e54b603d', 'TS_ID': '202507TSTSTAb211053c', 'Project_exception_time_id': 'fb6ceb72', 'Quantity': 5.0, 'Note': '21/07/2025', 'Update': None, 'last_change': '2025-07-09T17:05:52', 'changed_by': 'nico.marien@sisusync.app'}]}"

    carbone_api_url = f"https://api.carbone.io/render/{template_id}"
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        json_payload
        print("carbone api url:", carbone_api_url)
        print("headers:", headers)
        print("json_payload:", json.dumps(json_payload, indent=2))
        response = requests.post(carbone_api_url, data=json_payload, headers=headers)
        response.raise_for_status()
        print("✅ Carbone render response JSON (NEW FLOW):", response.json())
        return response  # Full response object

    except requests.exceptions.HTTPError as http_err:
        return None
    except requests.exceptions.RequestException as req_err:
        return None
    except Exception as e:
        return None
# #****************************************************************
def call_carbone(access_token, json_payload, template_id):
    print("access_token",access_token)
    json_payload= json.dumps(json_payload)
    print("json_payload",json_payload)
    print("template_id",template_id)
    """
    Call the Carbone API to generate a document from a template.

    :param access_token: The access token for authentication
    :param url: The Carbone API URL
    :param data: The data to be used in the template
    :param template_id: The ID of the template
    :param template_name: The name of the template
    :param template_type: The type of the template (e.g., PDF, DOCX)
    :return: The response from the Carbone API
    """
    headers = {
    "Authorization": access_token,
    "Content-Type": "application/json",
    "Accept": "application/json"
    }
    try: 
        carbone_api_url= f"https://api.carbone.io/render/{template_id}"  # API base URL + template_id for Carbone
        response_from_carbone = requests.post(carbone_api_url, data=json_payload, headers=headers)
        response_from_carbone.raise_for_status()  # throws an error if the request failed
        print("######################################################################")
        print("RESPONS POST JSON TO CARBONE",response_from_carbone.json())
        if response_from_carbone.status_code == 401:
            # Token is likely expired or invalid
            return jsonify({"error": "Unauthorized: token invalid or expired"}), 401
        elif response_from_carbone.status_code == 403:
            # Token is valid but user is forbidden (wrong scopes, etc.)
            return jsonify({"error": "Forbidden: access denied"}), 403
        else:
            return jsonify({"error": f"HTTP error: {http_err}"}), 500
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"Request failed: {http_err}"}), 500

    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Request failed: {req_err}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

        
    return response_from_carbone
# #****************************************************************
def get_file_from_carbone(access_token, render_id):
    headers = {
        "Authorization": access_token,
        "Accept": "application/octet-stream"  # Expect binary data
    }
    
    carbone_api_url = f"https://api.carbone.io/render/{render_id}"  # API base URL + template_id for Carbone
    response_from_carbone = requests.get(carbone_api_url, headers=headers)
    
    if response_from_carbone.status_code == 200:
        print("######################################################################")
        print("SUCCESSFUL RETRIEVAL OF DOCUMENT")
        content_type = response_from_carbone.headers.get("Content-Type", "application/octet-stream")
        return response_from_carbone.content, content_type
    else:
        raise Exception(f"Failed to retrieve document: {response_from_carbone.status_code} - {response_from_carbone.text}")
# #****************************************************************