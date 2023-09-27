import os
import email
from email.header import decode_header

class EMLParser:

    def __init__(self, eml_file_path):
        self.eml_file_path = eml_file_path
        with open(self.eml_file_path, 'rb') as eml_file:
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

    def extract_body(self):
        body = ""
        if self.msg.is_multipart():
            for part in self.msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = self.msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return body

    def extract_header(self):
        headers = {}
        headers['Subject'] = self.decode_field(self.msg['Subject'])
        headers['Date'] = self.msg['Date']
        headers['From'] = self.decode_field(self.msg['From'])
        headers['To'] = self.decode_field(self.msg['To'])
        headers['In-Reply-To'] = self.msg['In-Reply-To']
        headers['References'] = self.msg['References']
        bcc_field = self.msg.get_all('bcc')
        headers['BCC'] = [self.decode_field(bcc) for bcc in bcc_field] if bcc_field else None
        return headers

    def decode_field(self, field):
        decoded_field = decode_header(field)[0][0]
        if isinstance(decoded_field, bytes):
            return decoded_field.decode('utf-8')
        return decoded_field

    def parse(self):
        headers = self.extract_header()
        body = self.extract_body()
        attachments = self.extract_attachments()
        return headers, body, attachments

    def save_attachments(self, save_dir='attachments'):
        os.makedirs(save_dir, exist_ok=True)
        for filename, _, body in self.extract_attachments():
            file_path = os.path.join(save_dir, filename)
            with open(file_path, 'wb') as attachment_file:
                attachment_file.write(body)