import os
import pandas as pd
from googleapiclient.discovery import build
from utils.auth import load_credentials
from utils.helpers import generate_filename, get_email_body, list_labels
from googleapiclient.errors import HttpError

G_CREDENTIALS_FILEPATH = "secrets/g_credentials.json"


def fetch_recent_emails(credentials, max_results=100):
    service = build('gmail', 'v1', credentials=credentials)
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    decoded_emails = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']
        label_ids = msg.get('labelIds', [])
        labels = [list_labels(service).get(label_id, label_id) for label_id in label_ids]  # Convert label IDs to names
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        recipients = next((header['value'] for header in headers if header['name'] == 'To'), None)
        date = next((header['value'] for header in headers if header['name'] == 'Date'), None)
        body = get_email_body(payload)

        decoded_emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'recipients': recipients,
            'date': date,
            'body': body,
            'labels': labels,
            'threadId': msg['threadId'],
            'messageId': next((header['value'] for header in headers if header['name'] == 'Message-ID'), None),
            'inReplyTo': next((header['value'] for header in headers if header['name'] == 'In-Reply-To'), None),
        })

    return decoded_emails


def _process_messages(service, messages):
    decoded_emails = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']
        label_ids = msg.get('labelIds', [])
        labels = [list_labels(service).get(label_id, label_id) for label_id in label_ids]  # Convert label IDs to names
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        recipients = next((header['value'] for header in headers if header['name'] == 'To'), None)
        date = next((header['value'] for header in headers if header['name'] == 'Date'), None)
        body = get_email_body(payload)

        decoded_emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'recipients': recipients,
            'date': date,
            'body': body,
            'labels': labels,
            'threadId': msg['threadId'],
            'messageId': next((header['value'] for header in headers if header['name'] == 'Message-ID'), None),
            'inReplyTo': next((header['value'] for header in headers if header['name'] == 'In-Reply-To'), None),
        })

    return decoded_emails


def fetch_all_emails(credentials):
    service = build('gmail', 'v1', credentials=credentials)
    decoded_emails = []
    total_emails_fetched = 0

    try:
        # Initial request to retrieve messages
        initial_results = service.users().messages().list(userId='me').execute()
        total_emails = initial_results.get('resultSizeEstimate', 0)
        messages = initial_results.get('messages', [])
        decoded_emails.extend(_process_messages(service, messages))
        total_emails_fetched += len(messages)
        print(f"Total emails fetched: {total_emails_fetched}/{total_emails}")

        # If there are more messages, make additional requests using nextPageToken
        while 'nextPageToken' in initial_results:
            page_token = initial_results['nextPageToken']
            additional_results = service.users().messages().list(userId='me', pageToken=page_token).execute()
            messages = additional_results.get('messages', [])
            decoded_emails.extend(_process_messages(service, messages))
            total_emails_fetched += len(messages)
            print(f"Total emails fetched: {total_emails_fetched}/{total_emails}")
            initial_results = additional_results

    except HttpError as error:
        print(f"An error occurred: {error}")

    return decoded_emails


    return decoded_emails



def test_fetch_emails():
    credentials = load_credentials(G_CREDENTIALS_FILEPATH)
    # recent_emails = fetch_recent_emails(credentials)
    recent_emails = fetch_all_emails(credentials)
    pd.DataFrame(recent_emails).to_csv(
        f"data/{generate_filename('betadfw_emails', 'csv')}", index=None
    )
    email_subjects = [str(email.get("subject")) for email in recent_emails]
    # print(email_subjects)
    return "<br>".join(email_subjects)
