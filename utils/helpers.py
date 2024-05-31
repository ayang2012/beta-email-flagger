import base64
from datetime import datetime
from googleapiclient.discovery import build


def generate_filename(prefix, extension):
    now = datetime.now()
    datetime_str = now.strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{datetime_str}.{extension}"
    return filename


def list_labels(service):
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    label_map = {label["id"]: label["name"] for label in labels}
    return label_map


def get_email_body(payload):
    body = ""
    
    if "parts" in payload:
        for part in payload["parts"]:
            if "body" in part and "data" in part["body"]:
                body_data = part["body"]["data"]
                body += base64.urlsafe_b64decode(body_data).decode("utf-8")
            elif "parts" in part:
                # Recursively get body from nested parts
                body += get_email_body(part)
    else:
        if "body" in payload and "data" in payload["body"]:
            body_data = payload["body"]["data"]
            body += base64.urlsafe_b64decode(body_data).decode("utf-8")
    
    return body


