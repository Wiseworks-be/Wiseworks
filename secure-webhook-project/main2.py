import requests
import base64
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def create_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    return service

def upload_file_to_drive(service, file_path, file_name):
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

def send_email_with_invoice(invoice_path, client_email):
    # You would use an SMTP library or service to send an email with the invoice attached
    # This is a placeholder for the email sending functionality
    print(f"Sending email to {client_email} with invoice: {invoice_path}")

# Example
 usagedef main():
    # Assume `webhook_data` is the data received from the webhook
    webhook_data = {
        "invoice": {
            "client": "Timothy Johnson",
            "items": [
                {"name": "Product A", "quantity": 2, "price": 100},
                {"name": "Product B", "quantity": 1, "price": 200}
            ]
        }
    }

    # Call Carbone API to generate the invoice
    # placeholder
    invoice_url = "https://api.carbone.io/v1/render"
    response = requests.post(invoice_url, json=webhook_data)
    invoice_content = response.content

    # Save  to a file
    invoice_path = "invoice.pdf"
    with open(invoice_path, "wb") as file:
        file.write(invoice_content)

    # Upload to Google Drive
    service = create_service()
    upload_file_to_drive(service, invoice_path, "Invoice.pdf")

    # Send email with invoice attached
    client_email = "client@example.com"
    send_email_with_invoice(invoice_path, client_email)

if __name__ == "__main__":
    main()