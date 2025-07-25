#************************************************************************************************
# THIS FLOW UPLOADS AN XML INVOICE TO INCOMING INVOICES IN WHC                                   *
#                                                                                               *
# params: no params                                                                             *
#                                                                                               *
# creteated by: Marc De Krock                                                                   *
# date: 20250611                                                                                *
#************************************************************************************************


from authentication_utils import upload_doc_from_memory, save_token, load_token
from webhook_utils_1 import send_push_notification, post_data_to_appsheet
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
#import streamlit as st
from flask import Request, render_template_string, request, jsonify
from urllib.parse import quote
from datetime import datetime, timezone

WHC_app_id = "397f3d50-89dc-46bb-b912-e52499e9b2f1"
WHC_app_access_key = "V2-ggEMV-znIzP-zanfl-m6Sxr-zre0X-55Mkm-oOMQM-qfaZ6"
app_name = "WiseHubCore-346984636"
peppol_incoming_xml_files= '1BkPmQjzQILdIz8x6UF51kHbBItErw5bq' #default folder under WisehubCore


def main(request: Request):
    HTML_FORM_1 = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload XML</title>
    </head>
    <body>
        <h2>Upload a PEPPOL XML Invoice</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xml" required>
            <br><br>
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    """

    HTML_FORM = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload PEPPOL XML Invoice</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f2f2f2;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .upload-container {
                background: #fff;
                padding: 2em 3em;
                border-radius: 10px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 800px;
                width: 100%;
            }
            h2 {
                color: #333;
            }
            input[type="file"] {
                margin-top: 1em;
            }
            #uploadBtn {
                margin-top: 1.5em;
                padding: 0.5em 1.5em;
                font-size: 1em;
                background: #007BFF;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            #uploadBtn:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            #result {
                margin-top: 2em;
                background: #f8f9fa;
                border: 1px solid #ccc;
                padding: 1em;
                border-radius: 6px;
                word-wrap: break-word;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="upload-container">
            <h2>Upload a PEPPOL XML Invoice</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" name="file" accept=".xml" required>
                <br>
                <input type="submit" id="uploadBtn" value="Upload">
            </form>
            <div id="result"></div>
        </div>
        
        <script>
            const form = document.getElementById('uploadForm');
            const resultDiv = document.getElementById('result');
            const uploadBtn = document.getElementById('uploadBtn');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                uploadBtn.disabled = true;
                uploadBtn.value = "Uploading...";
                uploadBtn.style.backgroundColor = "#17a2b8";  // Light blue

                const formData = new FormData(form);

                try {
                    const response = await fetch("", {
                        method: "POST",
                        body: formData
                    });
                    const result = await response.json();
                    resultDiv.innerText = "✅ Upload successful:\\n" + JSON.stringify(result, null, 2);
                    uploadBtn.value = "Upload Again";
                    uploadBtn.style.backgroundColor = "#28a745";  // Green
                } catch (err) {
                    resultDiv.innerText = "❌ Error uploading file:\\n" + err;
                    uploadBtn.value = "Try Again";
                    uploadBtn.style.backgroundColor = "#dc3545";  // Red
                } finally {
                    uploadBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """

    if request.method == 'GET':
        return render_template_string(HTML_FORM)

    if 'file' not in request.files:
        return "Missing 'file' in form-data", 400

    xml_file = request.files['file']

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print(root.tag)
        # Peppol uses namespaces; define them here to use in find/findall
        namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
        def get_text(xpath):
            element = root.find(xpath, namespaces)
            return element.text.strip() if element is not None and element.text else "-"
        # Define the invoice payload dictionary
        invoice_payload = {
        "invoice_id" : get_text(".//cbc:ID"),  # Use .// to search deeply
        "invoice_issuedate" : get_text(".//cbc:IssueDate"),
        "invoice_duedate": get_text(".//cbc:DueDate"),
        "documentcurrencycode" : get_text(".//cbc:DocumentCurrencyCode"),
        "invoiceperiod_startdate" : get_text(".//cbc:StartDate"),
        "invoiceperiod_enddate" : get_text(".//cbc:EndDate"),
        "invoicetypecode" : get_text(".//cbc:InvoiceTypeCode"),
        "buyerreference" : get_text(".//cbc:BuyerReference/cbc:ID"),
        "orderreference_id" : get_text(".//cbc:OrderReference/cbc:ID"),
        "orderreference_salesorderid" : get_text(".//cbc:OrderReference/cbc:SalesOrderID"),
        "asp_party_endpointid" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:EndpointID/cbc:Value"),
        "asp_party_partyname_name" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name"),
        "asp_party_postaladdress_streetname": get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:StreetName"),
        "asp_party_postaladdress_cityname" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CityName"),
        "asp_party_postaladdress_postalzone" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:PostalZone"),
        #"asp_party_postaladdress_countryname_se" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CountrySubentity"),
        "asp_party_postaladdress_country_identificationcode" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:Country/cbc:IdentificationCode"),
        #"asp_party_postaladdress_countryname" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:Country/cbc:Name"),
        "asp_party_partytaxscheme_companyid": get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"),
        "asp_party_partytaxscheme_taxscheme_id" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID"),
        "asp_party_partylegalentity_registrationname" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName"),
        "asp_party_partylegalentity_companyid" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID"),
        "asp_party_contact_name" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Name"),
        "asp_party_contact_telephone" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone"),
        "asp_party_contact_electronicmail" : get_text(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail"),
        "acp_party_eindpointid" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:EndpointID/cbc:Value"),
        "acp_party_partyname_name" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name"),
        "acp_party_postaladdress_streetname" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:StreetName"),
        "acp_party_postaladdress_cityname" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName"),
        "acp_party_postaladdress_postalzone" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:PostalZone"),
        #"acp_party_postaladdress_countryname_se" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CountrySubentity"),
        "acp_party_postaladdress_country_identificationcode" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:Country/cbc:IdentificationCode"),
        #"acp_party_postaladdress_countryname" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:Country/cbc:Name"),
        "acp_party_partytaxscheme_companyid" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"),
        "acp_party_partytaxscheme_taxscheme_id" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID"),
        "acp_party_partylegalentity_registrationname" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName"),
        "acp_party_partylegalentity_companyid" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID"),
        "acp_party_contact_name" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Name"),
        "acp_party_contact_telephone" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone"),
        "acp_party_contact_electronicmail" : get_text(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail"),
        "paymentmeans_paymentmeanscode" : get_text(".//cac:PaymentMeans/cbc:PaymentMeansCode"),
        "paymentmeans_paymentid" : get_text(".//cac:PaymentMeans/cbc:PaymentID"),
        "paymentmeans_payeefinancialaccount_id" : get_text(".//cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:ID"),
        "paymentmeans_payeefinancialaccount_name" : get_text(".//cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:Name"),
        #"invoice_duedate" : get_text(".//cac:PaymentMeans/cbc:PaymentDueDate"),
        "paymentmeans_payeefinancialaccount_financialinstitutionbranch_id" : get_text(".//cac:PaymentMeans/cac:PayeeFinancialAccount/cac:FinancialInstitutionBranch/cbc:ID"),
        "paymentterms_note" : get_text(".//cac:PaymentTerms/cbc:Note"),
        "taxtotal_taxamount" : get_text(".//cac:TaxTotal/cbc:TaxAmount"),
        "legalmonetarytotal_lineextensionsamount" : get_text(".//cac:LegalMonetaryTotal/cbc:LineExtensionAmount"),
        "legalmonetarytotal_taxexclusiveamount" : get_text(".//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount"),
        "legalmonetarytotal_taxinclusiveamount" : get_text(".//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount"),
        "legalmonetarytotal_payableamount" : get_text(".//cac:LegalMonetaryTotal/cbc:PayableAmount"),
        "paymentmeans_payeefinancialaccount_financialinstitutionbranch_id" : get_text(".//cac:PaymentMeans/cac:PayeeFinancialAccount/cac:FinancialInstitutionBranch/cbc:ID"),
        }
        invoice_payload_json = json.dumps(invoice_payload, indent=4)
        print("invoice_payload before cleaning = ", invoice_payload_json)
        #clean the payload (remove lines with None or "" or "-" as values)
        cleaned_payload = {k: v for k, v in invoice_payload.items() if v not in ("", None, "-")}
        invoice_payload = cleaned_payload
        invoice_payload_json = json.dumps(invoice_payload, indent=4)
        print("invoice_payload_json after cleaning = ", invoice_payload_json)
        
        #return jsonify({"status": "success", "root_tag": root.tag})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    print("XML file processed successfully, now save the data to the Appsheet table(s)")
    # Define the AppSheet parameters
    try:
        print("now add record to Apssheet table incoming invoices")
        user_settings= {"User role":"Super Administrator"}
        response = post_data_to_appsheet(table="incoming_invoice", rows=[invoice_payload], action="Add", selector=None, user_settings=user_settings, app_name=app_name, app_id=WHC_app_id, app_access_key=WHC_app_access_key)
        print("Response from AppSheet:", response.status_code, "BODY: ",response.text)
        if response.status_code != 200:
            return jsonify({"error": "Failed to post data to AppSheet"}), response.status_code
        if not response.text:
            return jsonify({"error": f"Failed to post data to AppSheet, table or record could not be created: {response.text}"}), response.status_code
        else:# the record is already there, so we will update it now
            response_json = json.loads(response.text)
            
        response_json = json.loads(response.text)
        incoming_invoice_id = response_json["Rows"][0].get("incoming_invoice_id", "")
        print("incoming_invoice_id = ", incoming_invoice_id)
        
        #NOW DO THE INVOICE LINES
        print("now add record(s) to Apssheet table incoming_invoices_line")
        invoice_lines = []
        for line in root.findall('.//cac:InvoiceLine', namespaces):
            invoiceline_id = line.find('cbc:ID', namespaces)
            invoiceline_note = line.find('cbc:Note', namespaces)
            invoiceline_invoicedquantity = line.find('cbc:InvoicedQuantity', namespaces)
            invoiceline_lineextensionamount = line.find('cbc:LineExtensionAmount', namespaces)
            invoiceline_item_description = line.find('cac:Item/cbc:Description', namespaces)
            invoiceline_item_name = line.find('cac:Item/cbc:Name', namespaces)
            invoiceline_item_classifiedtaxcategory_id = line.find('cac:Item/cac:ClassifiedTaxCategory/cbc:ID', namespaces)
            invoiceline_item_classifiedtaxcategory_percent = line.find('cac:Item/cac:ClassifiedTaxCategory/cbc:Percent', namespaces)
            invoiceline_item_classifiedtaxcategory_taxscheme_id = line.find('cac:Item/cac:ClassifiedTaxCategory/cac:TaxScheme/cbc:ID', namespaces)
            invoiceline_price_priceamount = line.find('cac:Price/cbc:PriceAmount', namespaces)

            row = {
                "incoming_invoice": incoming_invoice_id,
                "invoiceline_id": invoiceline_id.text if invoiceline_id is not None else None,
                "invoiceline_note": invoiceline_note.text if invoiceline_note is not None else None,
                "invoiceline_invoicedquantity": invoiceline_invoicedquantity.text if invoiceline_invoicedquantity is not None else None,
                "invoiceline_lineextensionamount": invoiceline_lineextensionamount.text if invoiceline_lineextensionamount is not None else None,
                "invoiceline_item_description": invoiceline_item_description.text if invoiceline_item_description is not None else None,
                "invoiceline_item_name": invoiceline_item_name.text if invoiceline_item_name is not None else None,
                "invoiceline_item_classifiedtaxcategory_id": invoiceline_item_classifiedtaxcategory_id.text if invoiceline_item_classifiedtaxcategory_id is not None else None,
                "invoiceline_item_classifiedtaxcategory_percent": invoiceline_item_classifiedtaxcategory_percent.text if invoiceline_item_classifiedtaxcategory_percent is not None else None,
                "invoiceline_item_classifiedtaxcategory_taxscheme_id": invoiceline_item_classifiedtaxcategory_taxscheme_id.text if invoiceline_item_classifiedtaxcategory_taxscheme_id is not None else None,
                "invoiceline_price_priceamount": invoiceline_price_priceamount.text if invoiceline_price_priceamount is not None else None,
            }
            invoice_lines.append(row)
 
        for line in invoice_lines:
            percent_str = line.get("invoiceline_item_classifiedtaxcategory_percent")
            if percent_str:
                try:
                    percent_float = float(percent_str) / 100
                    line["invoiceline_item_classifiedtaxcategory_percent"] = str(percent_float)
                except ValueError:
                    line["invoiceline_item_classifiedtaxcategory_percent"] = "0.0"      
        invoice_lines_json = json.dumps(invoice_lines, indent=4)
        print("invoice_lines_json = ", invoice_lines_json)   
        #selector = f"Filter(contacts,[hs_contact_id]= {to_delete_object_id})"
        #print("selector: ", selector)
        response = post_data_to_appsheet(table="incoming_invoice_line", rows=invoice_lines, action="Add", selector=None, user_settings=None, app_name=app_name, app_id=WHC_app_id, app_access_key=WHC_app_access_key)
        print("Response from AppSheet after writing the invoice lines: ", response.status_code, "BODY: ",response.text)
        if response.status_code != 200:
            return jsonify({"error": "Failed to post data to AppSheet"}), response.status_code
        if not response.text:
            return jsonify({"error": f"Failed to post data to AppSheet, table or record not found: {response.text}"}), response.status_code
        
        #NOW DO THE TAX SUBTOTALS
        tax_totals = []
        for taxtotal in root.findall('.//cac:TaxTotal', namespaces):
            for subtotal in taxtotal.findall('cac:TaxSubtotal', namespaces):
                taxable_amount = subtotal.find('cbc:TaxableAmount', namespaces)
                tax_amount = subtotal.find('cbc:TaxAmount', namespaces)
                tax_category_id = subtotal.find('cac:TaxCategory/cbc:ID', namespaces)
                tax_category_percent = subtotal.find('cac:TaxCategory/cbc:Percent', namespaces)
                tax_scheme = subtotal.find('cac:TaxCategory/cac:TaxScheme/cbc:ID', namespaces)

                row = {
                    "incoming_invoice": incoming_invoice_id,
                    "taxableamount": taxable_amount.text if taxable_amount is not None else None,
                    "taxamount": tax_amount.text if tax_amount is not None else None,
                    "taxcategory_id": tax_category_id.text if tax_category_id is not None else None,
                    "taxcategory_percent": tax_category_percent.text if tax_category_percent is not None else None,
                    "taxscheme": tax_scheme.text if tax_scheme is not None else None,
                }
                tax_totals.append(row)
        
        for line in tax_totals:
            percent_str = line.get("taxcategory_percent")
            if percent_str:
                try:
                    percent_float = float(percent_str) / 100
                    line["taxcategory_percent"] = str(percent_float)
                except ValueError:
                    line["taxcategory_percent"] = "0.0"   
                invoice_lines_json = json.dumps(invoice_lines, indent=4)
        print("invoice_lines_json including TAX SUBTOTALS = ", invoice_lines_json)   
        response = post_data_to_appsheet(table="incoming_invoice_tax_subtotals", rows=tax_totals, action="Add", selector=None, user_settings=None, app_name=app_name, app_id=WHC_app_id, app_access_key=WHC_app_access_key)
        print("Response from AppSheet after writing the invoice lines: ", response.status_code, "BODY: ",response.text)
        if response.status_code != 200:
            return jsonify({"error": "Failed to post data to AppSheet"}), response.status_code
        if not response.text:
            return jsonify({"error": f"Failed to post data to AppSheet, table or record not found: {response.text}"}), response.status_code                             
        
        #all ok so now save the XML file 
        print("Now saving the XML file to Google drive...")
        # Read XML file as bytes
        xml_file.seek(0)
        file_content = xml_file.read()

        print("Now saving the XML file to Google drive...")
        folder_id = peppol_incoming_xml_files
        mime_type = "application/xml"
        file_timestamp_iso = datetime.now(timezone.utc).isoformat()
        now = datetime.now(timezone.utc)
        file_timestamp = now.strftime("%Y%m%dT%H%M%S")
        filename = f"XML_PEPPOL_INC_INV_{file_timestamp}_{incoming_invoice_id}.xml"

        print("Uploading document to Google Drive..., folder_id: ", folder_id)
        upload_doc_from_memory(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
            folder_id=folder_id
        )
        print("End uploading DOCUMENT to Google Drive...")
        table_name="peppol_incoming_xml_files"
        file_name = filename
        html_name_for_file = filename
        peppol_xml_url = (
            "https://www.appsheet.com/template/gettablefileurl"
            + "?appName=" + quote(app_name)
            + "&tableName=" + quote(table_name)
            + "&fileName=" + quote(file_name)
            )
        peppol_xml_url_html = f'<a href="{peppol_xml_url}" target="_blank">{html_name_for_file}</a>'

        
        rows={
            "incoming_invoice_id": incoming_invoice_id,
            "peppol_xml_url":peppol_xml_url,
            "peppol_xml_url_html":peppol_xml_url_html
        }
        
        response = post_data_to_appsheet(table="incoming_invoice", rows=[rows], action="Edit", selector=None, user_settings=None, app_name=app_name, app_id=WHC_app_id, app_access_key=WHC_app_access_key)
        print("Response from AppSheet after writing the invoice lines: ", response.status_code, "BODY: ",response.text)
        if response.status_code != 200:
            return jsonify({"error": "Failed to post data to AppSheet"}), response.status_code
        if not response.text:
            return jsonify({"error": f"Failed to post data to AppSheet, table or record not found: {response.text}"}), response.status_code

        return jsonify({
            "status": "success",
            "message": "XML file processed and uploaded to Google Drive",
            "timestamp": file_timestamp_iso
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred while posting data to AppSheet: {str(e)}"}), 500


                