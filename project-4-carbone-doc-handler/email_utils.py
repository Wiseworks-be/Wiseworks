import smtplib
import os
import mimetypes
from email.message import EmailMessage
import base64




def send_email(subject, body, sender_email, sender_password, recipient_email,
               attachment_bytes=None, attachment_filename=None,
               smtp_server='smtp.gmail.com', smtp_port=587):
    """
    Sends an email with optional in-memory file attachment.

    Parameters:
    - subject (str): Email subject line
    - body (str): Email body text
    - sender_email (str): Sender's email address
    - sender_password (str): Sender's app password (for Gmail)
    - recipient_email (str): Recipient's email address
    - attachment_bytes (bytes, optional): File content as bytes
    - attachment_filename (str, optional): Filename to use for attachment
    - smtp_server (str): SMTP server address
    - smtp_port (int): SMTP port number
    """

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(body)

    if attachment_bytes and attachment_filename:
        # Guess MIME type based on filename
        mime_type, _ = mimetypes.guess_type(attachment_filename)
        maintype, subtype = (mime_type or 'application/octet-stream').split('/')

        msg.add_attachment(attachment_bytes, maintype=maintype, subtype=subtype, filename=attachment_filename)
        print(f"📎 Attached in-memory file: {attachment_filename}")

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("✅ Email sent successfully.")
            return True
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your email/app password.")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return False
