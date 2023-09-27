import os
import win32com.client
import re

class PSTParser:
    
    def __init__(self, pst_file_path):
        self.pst_file_path = pst_file_path
        self.emails = []

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', '', filename)

    def process_folder(self, folder, output_folder):
        for item in folder.Items:
            if item.Class == 43:  # 43은 메일 아이템
                try:
                    email_data = {
                        "Subject": item.Subject,
                        "Sender": item.SenderName,
                        "Receiver": item.To,
                        "Body": item.Body,
                        "Attachments": []
                    }
                    for attachment in item.Attachments:
                        sanitized_filename = self.sanitize_filename(attachment.FileName)
                        save_path = os.path.join(output_folder, sanitized_filename)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder, exist_ok=True)
                        attachment.SaveAsFile(save_path)
                        email_data["Attachments"].append(save_path)
                    self.emails.append(email_data)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

        for subfolder in folder.Folders:
            self.process_folder(subfolder, output_folder)

    def extract_emails(self, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        outlook.AddStore(self.pst_file_path)
        root_folder = outlook.Folders.GetLast()
        self.process_folder(root_folder, output_folder)
        return self.emails

if __name__ == "__main__":
    pst_file_path = r"C:\Users\xyg19\OneDrive\바탕 화면\백업JISOOLEE.pst"
    output_folder = "extracted_emails"
    parser = PSTParser(pst_file_path)
    emails = parser.extract_emails(output_folder)
    for email in emails:
        print(email)
