import os
import sqlite3
import hashlib
import time

start_dir = 'C:\\Users\\dswhd\\OneDrive\\문서\\디포 자료\\행복의류 증거데이터 v0811' 
# full_path = os.path.dirname(start_dir)

conn = sqlite3.connect('files.sqlite')  
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS dirTest (file_path TEXT, sha256 TEXT, created_time INTEGER, modified_time INTEGER, accessed_time INTEGER)')

def search_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
          
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() in extensions_to_find:
             
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                  
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                sha256 = sha256_hash.hexdigest()

                created_time = os.path.getctime(file_path)
                modified_time = os.path.getmtime(file_path)
                accessed_time = os.path.getatime(file_path)

     
                cursor.execute('INSERT INTO dirTest (file_path, sha256, created_time, modified_time, accessed_time) VALUES (?, ?, ?, ?, ?)', (file_path, sha256, created_time, modified_time, accessed_time))
                conn.commit()
                print(f'파일: {file_path}')


extensions_to_find = ['.pdf', '.eml', '.docx', '.xlsx']
search_files(start_dir)
conn.close()
