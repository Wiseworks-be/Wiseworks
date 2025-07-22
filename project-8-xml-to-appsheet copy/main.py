#************************************************************************************************
# THIS FLOW UPLOADS AN XML INVOICE TO ICOMING INVOICES IN WHC                                   *
#                                                                                               *
# params: no params                                                                             *
#                                                                                               *
# creteated by: Marc De Krock                                                                   *
# date: 20250611                                                                                *
#************************************************************************************************


from authentication_utils import upload_doc_from_memory, save_token, load_token
from webhook_utils_1 import send_push_notification, post_data_to_appsheet
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
#import streamlit as st
from flask import Request, render_template_string, request, jsonify

WHC_app_id = "397f3d50-89dc-46bb-b912-e52499e9b2f1"
WHC_app_access_key = "V2-ggEMV-znIzP-zanfl-m6Sxr-zre0X-55Mkm-oOMQM-qfaZ6"
app_name = "WiseHubCore-346984636"
incoming_peppol_files= '1BkPmQjzQILdIz8x6UF51kHbBItErw5bq' #default folder under WisehubCore




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
        # Read XML file as bytes
        file_content = xml_file.read()

        print("Now saving the XML file to Google drive...")
        folder_id = incoming_peppol_files
        mime_type = "application/xml"
        filename = "TEST_upload_xml.xml"

        print("Uploading document to Google Drive..., folder_id: ", folder_id)
        upload_doc_from_memory(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
            folder_id=folder_id
        )
        print("End uploading DOCUMENT to Google Drive...")

        file_timestamp_iso = datetime.now(timezone.utc).isoformat()

        return jsonify({
            "status": "success",
            "message": "XML file processed and uploaded to Google Drive",
            "timestamp": file_timestamp_iso
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"An error occurred while saving data to Google Drive: {str(e)}"
        }), 500