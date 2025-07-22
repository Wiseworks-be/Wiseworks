
# MAIN.PY
#****************************************************************************
# THIS FLOW IS HANDLING INCOMING INVOICES TRIGGERED FROM A TICKSTAR WEBHOOK *
# IT HANDLES: INVOICES, CREDIT NOTES AND SB INVOICES                        *
#                                                                           *
# IT DECODES THE JSON MESSAGE FROM TICKSTAR                                 *
# IT GETS THE XML DOCUMENT FROM TICKSTAR                                    *
# IT SENDS THE XML FILE TO THE RELEVANT FUNCTION FOR FURTHER PROCESSING     *
#                                                                           *
#                                                                           *
# creteated by: Marc De Krock                                               *
# date: 20250613                                                            *
#****************************************************************************
# FROM OWN LIBS
from data_processing_utils import split_supplier_address_for_template, split_customer_address_for_template, clean_json_for_peppol
from authentication_utils import authenticate_drive, upload_xml_memory, save_token, load_token
from tickstar_utils import call_tickstar_api
from webhook_utils_1 import send_push_notification, post_data_to_appsheet_whc
# IMPORTS
import uuid
import functions_framework
import os
import re
import pandas as pd
import json
import xml.etree.ElementTree as ET
import google.auth
# FROM OTHER LIBS
from datetime import datetime, timezone
from flask import request, Response, jsonify
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote



"""
# Constants definition
TOKEN_FILE = Path("token_cache.json")
Instance_id_invoice = "Invoice-2::Invoice"
Instance_id_creditnote = "CreditNote-2::CreditNote"
Instance_id_Selfbilling = "Invoice-2::Invoice"
Process_nr_invoice = "01:1.0"
Process_nr_creditnote = "01:1.0"
Process_nr_Selfbilling = "06:1.0"


#************** HERE THE FLOW STARTS ***********************
#**SECRETS SECTION**
_, project_id = google.auth.default()
print("Project ID: ", project_id)
secret_value="^Yfz1R6BsD#KjmWp9@uCV83+OQtwcEbZPiFHaUL!M5xAqJhNX*GTo72v$lnRydk0gzseY#bKP4Q^mwdnMT"

#**GET BASEPATH
base_path = Path(os.getcwd())
print("Working directory:", os.getcwd())
#base_path = Path(__file__).parent
# Setup Jinja2 environment
env = Environment(
    loader=FileSystemLoader(base_path / "templates"),
    autoescape=select_autoescape(['xml'])
)
#template = env.get_template("my_template.xml.j2")
template = env.get_template("peppol_compliant_invoice_with_jinja_placeholders_1.xml")
"""

#************** HERE THE FLOW STARTS ***********************
#**SECRETS SECTION**
_, project_id = google.auth.default()
print("Project ID: ", project_id)
secret_value="^Yfz1R6BsD#KjmWp9@uCV83+OQtwcEbZPiFHaUL!M5xAqJhNX*GTo72v$lnRydk0gzseY#bKP4Q^mwdnMT"

#** URL ENTRY POINT FOR THE CLOUD FUNCTION **
@functions_framework.http
def main(request):
    incoming_key = request.headers.get("Appkey")
    print("Incoming key: ", incoming_key)
    print("Secret value: ", secret_value)
    if incoming_key != secret_value:
        print("Invalid key")
        return jsonify({"error": "Invalid key"}), 403
    print("Valid key")
    if request.method != "POST":
        return jsonify({"error": "Only POST requests are allowed, you stupid"}), 405
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Normalize JSON (flatten nested dicts/lists)
    try:
        entry_timestamp = datetime.now(timezone.utc).isoformat()
        random_uuid = str(uuid.uuid4())
        print("data", json.dumps(data, indent=2))
        print("______________________________________________")
        # SHOW timestamp and UUID, add later to the XML
        print("timestamp: ", entry_timestamp)
        print("random_uuid: ", random_uuid)
        print("______________________________________________")
        #**************************************************
  
        
        print("**** START COLLECTING DATA FOR VAT CALCULATION AND ADDING THEM TO THE JSON ****")
        # `data` is your original JSON dictionary
        invoice_lines = data.get("Invoice lines", [])

        def parse_currency(value):
            return float(re.sub(r"[^\d.,]", "", value).replace(",", "").strip())

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
            vat_percent = line.get("P_vat_percentage", "0.00%").replace("%", "").strip()
            tax_cat_id = line.get("P_vat_category", "S")  # Default if missing
            ex_vat = parse_currency(line.get("Total ex VAT", "0"))
            vat = parse_currency(line.get("Total VAT", "0"))
            tax_exemption_reason = line.get("vat_exemption_reason_code", "")

            key = (vat_percent, tax_cat_id)
            subtotal = totals_by_tax_category[key]
            subtotal["TaxableAmount"] += ex_vat
            subtotal["TaxAmount"] += vat
            subtotal["TaxCategory_ID"] = tax_cat_id
            subtotal["TaxCategory_Percent"] = vat_percent
            subtotal["TaxExemptionReason"] = tax_exemption_reason
        # Convert grouped data to a list
        data["TaxSubtotal"] = [
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
        print("**** END COLLECTING DATA FOR VAT CALCULATION AND ADDING THEM TO THE JSON ****")
        # PREPROCESS THE JSON DATA
        """data = replace_empty_values(data)
        data = normalize_keys(data)
        print("NORMALIZED: ", json.dumps(data, indent=2))
        data = reformat_dates_in_json(data, "%m/%d/%Y", "%Y-%m-%d")
        data = clean_vat_in_json(data)
        data = clean_money_in_json(data)
        data = capitalize_keys(data)"""
        invoice_data = clean_json_for_peppol(data)
    except Exception as e:
        return jsonify({"error": f"Failed to normalize JSON: {str(e)}"}), 500
    supplier_address_parts = split_supplier_address_for_template(data["P_supplier_address"])
    print("supplier_address_parts", json.dumps(supplier_address_parts, indent=2))
    print("______________________________________________")
    customer_address_parts = split_customer_address_for_template(data["P_customer_address"])
    print("customer_address_parts", json.dumps(customer_address_parts, indent=2))
    print("______________________________________________")
    
    # Show the normalized JSON data
    print("invoice_data", json.dumps(invoice_data, indent=2))
    print("______________________________________________")
    
    # Render XML from template
    print("xml_output", template.render(invoice=invoice_data))
    print("______________________________________________")
    
    #Check invoice type:
    if invoice_data["P_invoice_typecode"] == "380": #380 = peppol commercial invoice
        instance_id = Instance_id_invoice
        process_nr = Process_nr_invoice
    elif invoice_data["P_invoice_typecode"] == "381": #381 = peppol credit note
        instance_id = Instance_id_creditnote
        process_nr = Process_nr_creditnote
    elif invoice_data["P_invoice_typecode"] == "389": #389 = peppol self billed invoice
        instance_id = Instance_id_Selfbilling
        process_nr = Process_nr_Selfbilling
    else:
        return jsonify({"error": "Unknown invoice type"}), 400
    
    xml_output = template.render(invoice=invoice_data, 
                                 paymentmeans_code = "30", 
                                 randomUUID = random_uuid, 
                                 isoTimestamp = entry_timestamp, 
                                 trial_participant_id = "0007:9999004021", 
                                 TEST_supplier_endpoint = "9482348239847239874", 
                                 TEST_customer_endpoint = "FR23342",  
                                 **supplier_address_parts,
                                 **customer_address_parts,
                                 doc_instance_id=instance_id,
                                 doc_process_nr=process_nr
                                 )
    # **customer_address_parts means unpacking the dictionary into keyword arguments, is much quicker
    xml_output = xml_output.replace('<cbc:TaxExemptionReason>-</cbc:TaxExemptionReason>', '')
    xml_payload = xml_output.encode('utf-8')
    print("xml_payload =", xml_payload)
    #return(xml_payload, 200, {'Content-Type': 'application/xml'})

    # --- MAIN ---
    #OK, NOW UPLOAD THE XML TO GOOGLE DRIVE
    print("Uploading XML to Google Drive...")
    #** PREPARE THE FILENAME AND FOLDER ID **
    # 👇 Replace this with your real folder ID
    peppol_xml_files = '14cSev_C8w7fuYgU56__ijGoMuLMb3Rqh' #folder under WisehubCore
    #peppol_xml_files = '1vUKgQMKLPQMb3nACFRyT5mYg4-WV6lp8' #folder in root drive Petrol Cave
    TEST_PYTHON_SAVE_FILE = '1bKdJ8RF6WVPPVrWkyCqv_p6zPU-9jxEG' #folder in root drive MDK
    folder_id = peppol_xml_files
    now = datetime.now(timezone.utc)
    file_timestamp = now.strftime("%Y%m%dT%H%M%S")
    file_timestamp_iso = now.isoformat()
    invoice_id = invoice_data.get("Invoice_ID", "")
    sb_invoice_id = invoice_data.get("Sb_invoice_ID", "")
    if invoice_id:
        filename = f"XML_PEPPOL_INV_{file_timestamp}_{invoice_id}.xml"
    elif sb_invoice_id:
        filename = f"XML_PEPPOL_SB_{file_timestamp}_{sb_invoice_id}.xml"
    else:
        filename = f"XML_PEPPOL_NULL_{file_timestamp}_NO_ID.xml"

    xml_content = xml_output
    #xml_content = '<root><message>Hello from memory!</message></root>'
    print("Uploading XML to Google Drive..., folder_id: ", folder_id)
    drive_service = authenticate_drive()
    upload_xml_memory(drive_service, filename, xml_content, folder_id)
    #XML is uploaded to Google Drive, now we can send it to the Tickstar API
    print("End uploading XML to Google Drive...")

    #NOW DO THE TICKSTAR API CALL
    # Select project secrets
    print("NOW DO THE TICKSTAR API CALL")
    token = load_token()
    response= call_tickstar_api(token, xml_payload)
    response_data = response.json()
    print("response_data", json.dumps(response_data, indent=2))
    tickstar_timestamp = now.isoformat()

    transaction_status_code = response.status_code
    transaction_id = response_data.get("transactionId", "")
    transaction_error_title = response_data.get("type", "")
    transaction_error_type = response_data.get("type",  "")
    transaction_error_detail = response_data.get("detail",  "")
    print("transaction_id: ", transaction_id)
    print("transaction_status: ", transaction_status_code)
    print("transaction_error_title: ", transaction_error_title)
    print("transaction_error_type: ", transaction_error_type)
    print("transaction_error_detail: ", transaction_error_detail)
    
    
    #** PREPARE DATA FOR APPSHEET CALL TO CREATE RECORD **
    invoice_id = invoice_data.get("Invoice_ID", "")
    sb_invoice_id = invoice_data.get("Sb_invoice_id", "")
    table = "peppol_transactions"
    folder_table = "peppol_xml_files"
    html_name_for_file = filename
    
    #** prepare the url for the file saved in Google Drive **
    # Sample values (replace these with your actual values)
    app_name = "WiseHubCore-346984636"
    table_name = folder_table
    file_name = filename  
    xml_url = (
        "https://www.appsheet.com/template/gettablefileurl"
        + "?appName=" + quote(app_name)
        + "&tableName=" + quote(table_name)
        + "&fileName=" + quote(file_name)
        )
    xml_url_html = f'<a href="{xml_url}" target="_blank">{html_name_for_file}</a>'
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
        "p_transaction_status_code": str(transaction_status_code or ""),
        "p_transaction_id": str(transaction_id or ""),
        "p_transaction_error_title": str(transaction_error_title or ""),
        "p_transaction_error_type": str(transaction_error_type or ""),
        "p_transaction_error_detail": str(transaction_error_detail or ""),
        "transaction_timestamp": str(tickstar_timestamp or ""),
        "xml_file_creation_timestamp": str(file_timestamp_iso or ""),
        "xml_url": str(xml_url or ""),
        "xml_url_html": str(xml_url_html or "")
         }
    ]
    }
    print("JSON FOR APPSHEET: ", json.dumps(data, indent=2))
    #*********************************************************
    response = post_data_to_appsheet_whc(table, data)
    #*********************************************************
    print("Status Code from add line to ", table,":", response.status_code)
    print("Response JSON:", response.json())
    data=response.json()
    print("data", json.dumps(data, indent=2))


    #select sertain keys
    '''if data:
        selected = {
            "invoice_nr": data[0]["invoice_nr"],
            "project_id": data[0]["project_id"],
            "sb_invoice_id": data[0]["sb_invoice_id"]
        }
        print(json.dumps(selected, indent=2))
    else:
        print("No data returned in response.")'''

    
    #Send push notification
    
    return jsonify({"project_id":project_id,"message": "XML sent successfully", "response": response.json()}), 200