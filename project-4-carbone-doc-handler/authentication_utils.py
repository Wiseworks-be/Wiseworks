from pathlib import Path
import time
import json
import os
#for the filesaves to Google drive
from io import BytesIO
#import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
#from google.cloud import secretmanager

#*******************************************************
# Use full drive scope for uploading files
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = 'service-account.json'

# Step 1: Authenticate using service account
def authenticate_drive():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)

# Step 2: Upload doc from memory to specific folder
def upload_doc_from_memory(file_content, filename, mime_type, folder_id):
    drive_service = authenticate_drive()
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    buffer = BytesIO(file_content)
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name',
        supportsAllDrives=True  # Important for Shared Drives!
    ).execute()
    print(f"✅ Uploaded '{uploaded_file.get('name')}' to Google folder. File ID: {uploaded_file.get('id')}")


"""def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")"""
#*****************************************************