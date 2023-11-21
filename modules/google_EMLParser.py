import os
import email
from email.header import decode_header
from email.utils import parseaddr

class google_EMLParser:

    def __init__(self, eml_file_path):
        with open(eml_file_path, 'rb') as eml_file:
            self.msg = email.message_from_binary_file(eml_file)

    def extract_attachments(self):
        attachments = []
        for part in self.msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode('utf-8')
                content_type = part.get_content_type()
                body = part.get_payload(decode=True)
                attachments.append((filename, content_type, body))
        return attachments

    @staticmethod
    def _decode_header_value(header_value):
        decoded = decode_header(header_value)[0][0]
        if isinstance(decoded, bytes):
            return decoded.decode('utf-8')
        return decoded

    def extract_name_email(self, header):
        name, email_address = parseaddr(header)
        if name:
            name = self._decode_header_value(name)
        if email_address:
            email_address = self._decode_header_value(email_address)
        return name, email_address

    def extract_recipients(self, header):
        names = []
        emails = []
        if header:
            recipients = header.split(',')
            for recipient in recipients:
                name, email_address = self.extract_name_email(recipient)
                if name:
                    names.append(name)
                if email_address:
                    emails.append(email_address)
        return names, emails

    def extract_body(self):
        body = ""
        if self.msg.is_multipart():
            for part in self.msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = self.msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return body

    def parse(self):
        # Headers
        subject = self._decode_header_value(self.msg['Subject'])
        date = self._decode_header_value(self.msg['Date'])
        from_name, from_email = self.extract_name_email(self.msg.get('From'))
        to_names, to_emails = self.extract_recipients(self.msg.get('To'))
        cc_names, cc_emails = self.extract_recipients(self.msg.get('Cc'))
        message_id = self._decode_header_value(self.msg.get('Message-ID'))
        body = self.extract_body()
        attachments = self.extract_attachments()
        return {
            'Subject': subject,
            'Date': date,
            'From_Name': from_name,
            'From_Email': from_email,
            'To_Names': to_names,
            'To_Emails': to_emails,
            'Cc_Names': cc_names,
            'Cc_Emails': cc_emails,
            'Message_ID': message_id,
            'Body': body,
            'Attachments': attachments
        }
