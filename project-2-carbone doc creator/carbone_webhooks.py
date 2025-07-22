from authentication_utils import save_token
import uuid
import requests
import json
from flask import request, Response, jsonify

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
    except requests.exceptions.HTTPError as http_err:
        return 
        if response_from_carbone.status_code == 401:
            # Token is likely expired or invalid
            return jsonify({"error": "Unauthorized: token invalid or expired"}), 401
        elif response_from_carbone.status_code == 403:
            # Token is valid but user is forbidden (wrong scopes, etc.)
            return jsonify({"error": "Forbidden: access denied"}), 403
        else:
            return jsonify({"error": f"HTTP error: {http_err}"}), 500

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