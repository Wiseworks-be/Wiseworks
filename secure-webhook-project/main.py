import os
import json
from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']

app = Flask(__name__)

# AUTHENTICATE AND SAVE token.json
def get_credentials():
    creds = None
    if os.path.exists('credentials.json.json'):
        creds = Credentials.from_authorized_user_file('credentials.json.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('credentials.json.json', 'w') as token:
            token.write(creds.to_json())
    return creds

#  Sample endpoint to test the webhook


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # 2. Save the content as a document
    file_path = "output.txt"
    with open(file_path, "w") as f:
        f.write(message)

    # 3. send to Google Drive
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {'name': 'WebhookOutput.txt'}
    media = MediaFileUpload(file_path, mimetype='text/plain')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return jsonify({"status": "File_uploaded", "file_id": file.get('id')}), 200

if __name__ == '__main__':
    app.run(port=50000)