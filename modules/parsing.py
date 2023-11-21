
import os
import hashlib
import sqlite3
import time
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import zipfile
from doc_extractor import DOCExtractor
from hwp_extractor import HWPExtractor
from docx_extractor import DOCXExtractor
from pptx_extractor import PPTXExtractor
from xlsx_extractor import XLSXExtractor

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == ".doc":
            extractor = DOCExtractor(file_path)
            text = extractor.get_text()
        elif ext == ".docx":
            extractor = DOCXExtractor(file_path)
            text = extractor.get_text()
        elif ext == ".pptx":
            extractor = PPTXExtractor(file_path)
            text = extractor.get_text()
        elif ext == ".xlsx":
            extractor = XLSXExtractor(file_path)
            text = extractor.get_text()
        elif ext == ".hwp":
            extractor = HWPExtractor(file_path)
            text = extractor.get_text()
        else:
            print(f"지원하지 않는 파일 형식: {file_path}")
    except Exception as e:
        print(f"텍스트 추출 중 오류 발생: {file_path}, {e}")

    return text.strip()


def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_creation_time(file_path):
    file = Path(file_path)
    return time.ctime(file.stat().st_ctime)


def save_to_db(conn, file_info):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (file_path, hash_value, plain_text, m_time, a_time, c_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', file_info)
    conn.commit()


def process_files(directory, whitelist, conn):
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.startswith("~$") or filename.endswith(".tmp"):
                continue
            
            file_path = os.path.join(foldername, filename)

            if file_path.lower().endswith(whitelist):
                try:
                    file_text = extract_text(file_path)
                    hash_value = calculate_hash(file_path)
                    c_time = get_creation_time(file_path)
                    stat = os.stat(file_path)
                    m_time = time.ctime(stat.st_mtime)
                    a_time = time.ctime(stat.st_atime)
                    
                    file_info = (file_path, hash_value, file_text, m_time, a_time, c_time)
                    save_to_db(conn, file_info)

                except Exception as e:
                    print(f"파일 처리 중 오류 발생: {file_path}, {e}")

# DB 연결 및 테이블 생성
conn = sqlite3.connect('parsing.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value TEXT NOT NULL,
    plain_text TEXT,
    m_time TEXT NOT NULL,
    a_time TEXT NOT NULL,
    c_time TEXT NOT NULL
)
''')

# 화이트리스트 확장자
whitelist_extensions = ('.hwp', '.doc', '.docx', '.xlsx', '.pptx', '.pdf')

# 파일 처리
process_files('C:\\Users\\xyg19\\OneDrive\\바탕 화면', whitelist_extensions, conn)

# DB 연결 종료
conn.close()

