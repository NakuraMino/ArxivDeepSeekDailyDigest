import os.path
import base64
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from types import SimpleNamespace
import yaml


class GmailClient:
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    def __init__(self, credentials_file="configs/credentials.json",
                 token_file="configs/token.json",
                 email_cfg="configs/email.yaml"):
        with open(email_cfg, "r") as file:
           self.cfg = SimpleNamespace(**yaml.safe_load(file))
        self.sender = self.cfg.sender
        self.to = self.cfg.receiver
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate and authorize the user."""
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("gmail", "v1", credentials=self.creds)

    def create_message(self, papers, html=True):
        """Create a message for sending an email."""
        message = MIMEMultipart()
        today = (datetime.today() - timedelta(days=1)).strftime("%m%d")
        message["Subject"] = f"{today} Arxiv Paper Daily Digest"
        message["From"] = self.sender
        message["To"] = self.to
        body = ""
        for i, result in enumerate(papers):
            title = f"<h3><b>{i+1}.</b> {result.title}</h3>\n"
            authors = f"<p><b>Authors:</b> {result.authors}</p>\n"
            summary = f"<p><b>Summary:</b> {result.summary}</p>\n"
            url = f"<p><b>URL:</b> <a href='{result.url}'>{result.url}</a></p>\n"
            paragraph = title + authors + summary + url + "</div>"
            body += paragraph
        if html:
            message.attach(MIMEText(body, "html"))
        else:
            message.attach(MIMEText(body, "plain"))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_data = {"raw": raw_message}
        return message_data

    def send_email(self, papers):
        """Send an email message."""
        try:
            message = self.create_message(papers)
            sent_message = self.service.users().messages().send(userId="me", body=message).execute()
            print(f"Message Id: {sent_message['id']}")
            return sent_message
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None


def main():
    gmail = GmailClient()
    gmail.send_email([])


if __name__ == "__main__":
    main()
