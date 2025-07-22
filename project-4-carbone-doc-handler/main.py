
# MAIN.PY
#********************************************************************************************************************************************
# THIS FLOW HANDLES ALL CREATE DOC REQUESTS FROM ANY SYSTEM USING CARBONE                                                  
#                                                                                                                          
# params: baseurl?template_id=template_id&mode=test|prod&folder_id=folder_id&filename=none|filename|generate,sender=WHC|petrolcave|raw... 
# in body: JSON data to be used for the template                                                                           
#                                                                                                                          
# creteated by: Marc De Krock                                                                                              
# date: 20250516
# change history:
# 20250708: added "raw" for jsons that need no pre-processing, now specific for Sisu                                                                                                           
#********************************************************************************************************************************************

from data_processing_utils import split_supplier_address_for_template, split_customer_address_for_template, clean_json_data_for_carbone,convert_string_numbers_in_json
from authentication_utils import upload_doc_from_memory
from carbone_webhooks import get_file_from_carbone,call_carbone_render
from email_utils import send_email
import base64
import json
import os
import re
from datetime import datetime, timezone
from webhook_utils_1 import send_push_notification, post_data_to_appsheet_whc, post_data_to_appsheet_pc
import uuid
import functions_framework
from flask import jsonify
from pathlib import Path
import pandas as pd
import json
from collections import defaultdict
import xml.etree.ElementTree as ET
from urllib.parse import quote
import google.auth



# Constants
#WHC_app_id = "397f3d50-89dc-46bb-b912-e52499e9b2f1"
#WHC_app_access_key = "V2-ggEMV-znIzP-zanfl-m6Sxr-zre0X-55Mkm-oOMQM-qfaZ6"
#app_name = "WiseHubCore-346984636"
secret_value="7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d901fa57c3de8196a54be1f9a84cb29c07915320c6de5f13e98b94298c83ae374bcbb6"
print("secret_value: ", secret_value)
#carbone stuff
carbone_template_id = "17914f9afc4be4d9c33c4559cef936db44d3f267dd4187b9e7ce11893eba53ae"
carbone_access_token_test = "test_eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxMDMyNTAyMzM5Mjg3MTIwNzQxIiwiYXVkIjoiY2FyYm9uZSIsImV4cCI6MjM5NDc5OTA3MCwiZGF0YSI6eyJ0eXBlIjoidGVzdCJ9fQ.AeNwsovwdLdyPAqJ16IjPSOjImuv5Yj0y8mdKJDApZlP0j3XD1T90x1wQSL5AkWU42d6iC3dWOLAjdn9zCUBHQWeAMkP46CN_pMj2NT3acUU7TSIGI1U6a5dRcNXeE4t_WLguijWVCm33Nkus1-ap_bp7GL84eMnpvCHXJ8VVUrqt2tS"
carbone_access_token_prod = "test_eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxMDMyNTAyMzM5Mjg3MTIwNzQxIiwiYXVkIjoiY2FyYm9uZSIsImV4cCI6MjM5NDc5OTA3MCwiZGF0YSI6eyJ0eXBlIjoidGVzdCJ9fQ.AeNwsovwdLdyPAqJ16IjPSOjImuv5Yj0y8mdKJDApZlP0j3XD1T90x1wQSL5AkWU42d6iC3dWOLAjdn9zCUBHQWeAMkP46CN_pMj2NT3acUU7TSIGI1U6a5dRcNXeE4t_WLguijWVCm33Nkus1-ap_bp7GL84eMnpvCHXJ8VVUrqt2tS"
carbone_invoice_files = '1KPlWNj5MADnQNuaNW_Khrx_RZj1ZE7PP' #default folder under WisehubCore
carbone_filename="CarboneReport.pdf" #default filename

#SISU
carbone_template_id_sisu_ts = "11dc5f880d56434b9ffe684b4eb5e1ebaf1e98ec9c05b5534c6f02a751cfbd59"
carbone_access_token_test_sisu = "test_blqablabla"
carbone_access_token_prod_sisu = "eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxMTI2MDAyMjg2OTYzODg2NDczIiwiYXVkIjoiY2FyYm9uZSIsImV4cCI6MjQwNTk0NTgwNiwiZGF0YSI6eyJ0eXBlIjoicHJvZCJ9fQ.AH3LrsZ92_uHFwm3H7xvUs4UkH39FOz7qw-GT0Dr67tMGqMDkwhQqBneudcqcJwsVjiij8kI0WmX1g7IwMu8MCfyAAyVNjriZPY_O3tZlA42bClXigwUlYbtt6qUiVFNK9EmAQOfVjEfRq2peT75LaLUMKG4k1oK_iD92cNhNQkPUYsr"
carbone_invoice_files_sisu = '1KPlWNj5MADnQNuaNW_Khrx_RZj1ZE7PP' #default folder under WisehubCore (for test)


# ************** HERE IT STARTS ***********************
#**SECRETS**
_, project_id = google.auth.default()
print("Project ID: ", project_id)
"""PROJECT_ID = project_id
SECRET_ID = "Appkey_A1"

secret_value = get_secret(SECRET_ID, PROJECT_ID)

print("****************My secret value:", secret_value)"""


@functions_framework.http
def main(request):
    #TESTRUN
    test_run=request.args.get('test')
    if test_run:
        print("Test run, skipping security checks and processing")
        return jsonify({"message": "Test run, no processing done"}), 200
    # SECURITY CHECK
    incoming_key = request.headers.get("AppKey")
    sender = request.args.get('sender')
    print("***Incoming key: ", incoming_key)
    print("***Secret value: ", secret_value)
    print("***Sender: ", sender)
    if incoming_key != secret_value:
        print("Invalid key")
        return jsonify({"error": "Invalid key"}), 403
    print("Valid key")
    # END SECURITY CHECK
    template_id=request.args.get("template_id")
    print("***template_id: ", template_id)
    mode=request.args.get("mode")
    print("***mode: ", mode)
    carbone_template_id = template_id
    if mode == "test":
        carbone_access_token=carbone_access_token_test
    elif mode == "prod":
        carbone_access_token=carbone_access_token_prod
    else:
        return jsonify({"error": "Invalid mode (prod or test not defined in params)"}), 400
    folder_id=request.args.get("folder_id")
    print("***folder_id: ", folder_id)
    if folder_id == None:
        folder_id=carbone_invoice_files #default folder 
        print("take the default folder....")
        
    arg_filename=request.args.get("filename")
    print("***filename: ", arg_filename)
    if arg_filename == None:
        arg_filename=carbone_filename
        print("take the default filename....")
    if arg_filename == "generate":    
        arg_filename = f"CarboneReport_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    
    print("***filename: ", arg_filename)
    #**GET BASEPATH
    base_path = Path(os.getcwd())
    print("Working directory:", os.getcwd())

    #base_path = Path(__file__).parent

    # GET THE JSON BODY
    if request.method != "POST":
        return jsonify({"error": "Only POST requests are allowed, you stupid 😁"}), 405
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
        
    # Normalize JSON (flatten nested dicts/lists)
    try:
        entry_timestamp = datetime.now(timezone.utc).isoformat()
        random_uuid = str(uuid.uuid4())
        print("data 1", json.dumps(data, indent=2))
        print("______________________________________________")
        # SHOW timestamp and UUID, add later to the XML
        print("timestamp: ", entry_timestamp)
        print("random_uuid: ", random_uuid)
        print("______________________________________________")
        #**************************************************
        
        #****************************************************************
        #* THE JSON IS NOW COMPLETED, NOW CLEAN IT                      *
        #* SO IT MATCHES THE PEPPOL REQUIREMENTS                        *
        #* (eg. no currency symbols, dates in correct format, etc...)   *
        #****************************************************************        
        print("HOW DOES DATA LOOK LIKE BEFORE CLEANING: ", json.dumps(data, indent=2))
        cleaned_invoice_data = clean_json_data_for_carbone(data)
        print("CLEANED JSON: ", json.dumps(cleaned_invoice_data, indent=2))
        
        
        print("**** START COLLECTING DATA FOR VAT CALCULATION AND ADDING THEM TO THE JSON ****")
        # `data` is your original JSON dictionary
        invoice_lines = cleaned_invoice_data.get("Invoice_lines", [])

        #def parse_currency(value):
        #    return float(re.sub(r"[^\d.,]", "", value).replace(",", "").strip())

        print("invoice_lines are now:", json.dumps(invoice_lines, indent=2))
        if sender != "raw": # This is a placeholder to skip this section for testing, so now do it for all senders except "raw"
            # Use a dict to group subtotals by VAT rate and category ID
            totals_by_tax_category = defaultdict(lambda: {
                "TaxableAmount": 0.0,
                "TaxAmount": 0.0,
                "TaxCategory_ID": "",
                "TaxCategory_Percent": "",
                "TaxExemptionReasonCode": "",
                "TaxExemptionReason": "",
                "TaxScheme_ID": "VAT"  # Fixed as you specified
            })

            for line in invoice_lines:
                vat_percent = line.get("P_vat_percentage", 1.11)
                tax_cat_id = line.get("P_vat_category", "S")  # Default if missing
                ex_vat = line.get("Total ex VAT", 0)
                vat = line.get("Total VAT", 0)
                print("vat and ex_vat", vat, "   ",ex_vat)
                tax_exemption_reason = line.get("vat_exemption_reason_code", "")

                key = (vat_percent, tax_cat_id)
                subtotal = totals_by_tax_category[key]
                subtotal["TaxableAmount"] += ex_vat
                subtotal["TaxAmount"] += vat
                subtotal["TaxCategory_ID"] = tax_cat_id
                subtotal["TaxCategory_Percent"] = vat_percent
                subtotal["TaxExemptionReason"] = tax_exemption_reason
            # Convert grouped data to a list
            cleaned_invoice_data["TaxSubtotal"] = [
                {
                    "TaxableAmount": f"{totals['TaxableAmount']:.2f}",
                    "TaxAmount": f"{totals['TaxAmount']:.2f}",
                    "TaxCategory_ID": totals["TaxCategory_ID"],
                    "TaxCategory_Percent": totals["TaxCategory_Percent"],
                    "TaxScheme_ID": totals["TaxScheme_ID"],
                    "TaxExemptionReason": totals["TaxExemptionReason"]
                }
                for totals in totals_by_tax_category.values()      
                ] 
            print("data 2", json.dumps(cleaned_invoice_data, indent=2))
            print("data['TaxSubtotal']", json.dumps(cleaned_invoice_data["TaxSubtotal"], indent=2))
            print("**** END COLLECTING DATA FOR VAT CALCULATION AND ADDING THEM TO THE JSON ****")

    except Exception as e:
        return jsonify({"error": f"Failed to normalize JSON: {str(e)}"}), 500
    
    if sender != "raw":
        supplier_address_parts = split_supplier_address_for_template(cleaned_invoice_data["P_supplier_address"])
        print("supplier_address_parts", json.dumps(supplier_address_parts, indent=2))
        print("______________________________________________")
        customer_address_parts = split_customer_address_for_template(cleaned_invoice_data["P_customer_address"])
        print("customer_address_parts", json.dumps(customer_address_parts, indent=2))
        print("______________________________________________")
        
        cleaned_invoice_data.update(supplier_address_parts)
        cleaned_invoice_data.update(customer_address_parts)
        
        # Show the normalized JSON data
        print("invoice_data for CARBONE", json.dumps(cleaned_invoice_data, indent=2))
        print("______________________________________________")
        
        final_payload = {
        "data": cleaned_invoice_data,
        "convertTo": "pdf",
        "timezone": "Europe/Paris",
        "lang": "nl",
        "complement": {},
        "variableStr": "",
        "reportName": "document",
        "enum": {},
        "translations": {},
        "currencySource": "",
        "currencyTarget": "",
        "currencyRates": {},
        "hardRefresh": ""
        }
        
        print("final_payload", json.dumps(final_payload, indent=2))
    else: # when sender is "raw"
        final_payload = data #get the JSON directly from the incomming call
        carbone_access_token = carbone_access_token_prod_sisu
        carbone_template_id = carbone_template_id_sisu_ts
        folder_id = carbone_invoice_files_sisu
        print("xxxxxxxxx RAW Template_id = ", template_id)
        print("xxxxxxxxx RAW carbone_access_token = ", carbone_access_token)
        print("xxxxxxxxx RAW folder_id = ", folder_id)
        print("xxxxxxxxx RAW final_payload = ", json.dumps(final_payload, indent=2))
    
    
    # CALL CARBONE API
    print(">>>>>> NOW CALL CARBONE API <<<<<<")
    carbone_render_response = call_carbone_render(access_token=carbone_access_token, json_payload=final_payload, template_id=carbone_template_id)
    if carbone_render_response == None:
        return jsonify({"error": "Failed to call Carbone API"}), 500
    carbone_render_status = carbone_render_response.status_code
    #carbone_render_response_dict = json.loads(carbone_render_response)
    carbone_render_response=carbone_render_response.json()
    carbone_render_id = carbone_render_response.get("data", {}).get("renderId")
    carbone_render_success = carbone_render_response.get("success", False)
    print("carbone_render_id:xxxxxxxxxx ", carbone_render_response)
    print("carbone_render_id: ", carbone_render_id)
    print("carbone_render_response: ", carbone_render_success)
    print("carbone_render_status: ", carbone_render_status)
    
    print("ARG_FILENAME: ", arg_filename)
    
    #****************************************
    # CREATE THE FILENAME
    #****************************************
    if arg_filename=="generate":
        invoice_type = cleaned_invoice_data.get("Invoice_type", False)
        invoice_id = cleaned_invoice_data.get("Invoice_ID", "")
        arg_filename= f"{invoice_type}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_invoice_{invoice_id}"
    print("ARG_FILENAME: ", arg_filename)
    #GET THE FILE FROM CARBONE
    file_content, mime_type = get_file_from_carbone(access_token=carbone_access_token, render_id=carbone_render_id)
    print("mime_type: ", mime_type)
    print("file_content: ",file_content[:10])
    ext_map = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
    }
    extension = ext_map.get(mime_type, "")
    filename = f"{arg_filename}{extension}"
    print("***** Real filename: ", filename)
    
    # Save rendered document to Google Drive
    print("Uploading document to Google Drive..., folder_id: ", folder_id)
    upload_doc_from_memory(file_content=file_content, filename=filename, mime_type=mime_type, folder_id=folder_id)
    #XML is uploaded to Google Drive, now we can send it to the Tickstar API
    print("End uploading DOCUMENT to Google Drive...")
    # GET THE TIMESTAMP FOR THE FILE
    file_timestamp_iso = datetime.now(timezone.utc).isoformat()
    #****************************************
    # END CREATE THE FILENAME
    #****************************************


    
    #**********************************************************
    #** PREPARE DATA FOR APPSHEET CALL TO CREATE RECORD
    #**********************************************************
    if sender == "WHC" or sender == "": #do not process for petrolcave, only for WHC
        invoice_id = cleaned_invoice_data.get("Invoice_ID", "")
        sb_invoice_id = cleaned_invoice_data.get("Sb_invoice_ID", "")
        app_name = "WiseHubCore-346984636"
        table = "invoice_doc_transactions"
        folder_table = "carbone_invoice_files"
        html_name_for_file = filename
        
        #** prepare the url for the file saved in Google Drive **
        # Sample values (replace these with your actual values)
        table_name = folder_table
        file_name = filename  
        carbone_file_url = (
            "https://www.appsheet.com/template/gettablefileurl"
            + "?appName=" + quote(app_name)
            + "&tableName=" + quote(table_name)
            + "&fileName=" + quote(file_name)
            )
        carbone_file_url_html = f'<a href="{carbone_file_url}" target="_blank">{html_name_for_file}</a>'
        #** NOW STORE THE TICKSTAR RESPONSE IN THE APPSHEET TABLE  **
        #****************************************************************
        #table to address
        #table = "peppol_transactions"
        # Headers
        #none
        #JSON payload
        #`Add`: Adds a new row to the table.
        #`Delete`: Deletes existing rows from the table.
        #`Edit`: Updates existing rows in the table.
        #`Find`: Reads an existing row of the table.
        data = {
        "Action": "Add",
        "Properties": {
        "Locale": "en-US", 
        "Location": "51.159133, 4.806236", 
        "Timezone": "Central European Standard Time",
        #  "Selector": "Filter(SB invoices,[Customer]= SB20250003)",
        "UserSettings": {  "User role":"Super Administrator" }
        },
        "Rows": [
            {
            "invoice_id": str(invoice_id or ""),
            "sb_invoice_id": str(sb_invoice_id or ""),
            "carbone_render_status_code": str(carbone_render_status or ""),
            "carbone_render_message": str(carbone_render_success or ""),
            "carbone_render_id": str(carbone_render_id or ""),
            "carbone_template_id": str(carbone_template_id or ""),
            "transaction_timestamp": str(entry_timestamp or ""),
            "carbone_file_creation_timestamp": str(file_timestamp_iso or ""),
            "carbone_file_name": str(filename or ""),
            "carbone_file_folder_id": str(folder_id or ""),
            "carbone_file_url": str(carbone_file_url or ""),
            "carbone_file_url_html": str(carbone_file_url_html or "")
            }
        ]
        }
        print("JSON FOR APPSHEET: ", json.dumps(data, indent=2))
        #*********************************************************
        response = post_data_to_appsheet_whc(table, data)
        #*********************************************************
        print("Status Code from add line to: ", table,":", response.status_code)
        data=response.json()
        print("data", json.dumps(data, indent=2))
    elif sender == "petrolcave": #***** TO CHECK IF THIS IS WORKING FOR PETROLCAVE ****
        #** prepare the url for the file saved in Google Drive **
        # Sample values (replace these with your actual values)
        invoice_id = cleaned_invoice_data.get("Invoice_ID", "")
        app_name = "PetrolCaveAutohandel-346984636"
        table = "Invoices PC"
        folder_table = "ad_hoc_invoices_carbone"
        html_name_for_file = filename
        table_name = folder_table
        file_name = filename  
        carbone_file_url = (
            "https://www.appsheet.com/template/gettablefileurl"
            + "?appName=" + quote(app_name)
            + "&tableName=" + quote(table_name)
            + "&fileName=" + quote(file_name)
            )
        carbone_file_url_html = f'<a href="{carbone_file_url}" target="_blank">{html_name_for_file}</a>'
        print("*************carbone_file_url: ", carbone_file_url)
        #** NOW STORE THE TICKSTAR RESPONSE IN THE APPSHEET TABLE  **
        #****************************************************************

        # Headers
        #none
        #JSON payload
        #`Add`: Adds a new row to the table.
        #`Delete`: Deletes existing rows from the table.
        #`Edit`: Updates existing rows in the table.
        #`Find`: Reads an existing row of the table.
        data = {
        "Action": "Edit",
        "Properties": {
            "Locale": "en-US", 
            "Location": "51.159133, 4.806236", 
            "Timezone": "Central European Standard Time",
            #  "Selector": "Filter(SB invoices,[Customer]= SB20250003)",
            #  "UserSettings": {  "User role":"Super Administrator" }
            },
            "Rows": [
                {
                "Invoice ID": str(invoice_id or ""),
                "Invoice doc url": str(carbone_file_url or ""),
                "Invoice doc url html": str(carbone_file_url_html or "")
                }
            ]
        }
        print("JSON FOR APPSHEET (Petrol Cave app): ", json.dumps(data, indent=2))
        #*********************************************************
        response = post_data_to_appsheet_pc(table, data)
        #*********************************************************
        print("Status Code from add line to: ", table,":", response.status_code)
        data=response.json()
        print("data", json.dumps(data, indent=2))
    elif sender == "raw": #***** SENDER is "raw"  ****
        print("RAW")
        print("So finally now send email")
        encoded_pdf = base64.b64encode(file_content).decode('utf-8')
       # Prepare response JSON
        response_data = {
            "filename": filename,
            "mime_type": "application/pdf",
            "content_base64": encoded_pdf
         }
        return jsonify(response_data)
    #**********************************************************
    
    #Send push notification
    
    return jsonify({"project_id":project_id,"message": "document was created successfully"}), 200