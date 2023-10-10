import os
import hashlib
import sqlite3
import time
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import xml.etree.ElementTree as ET  # 수정: 별칭 ET 사용
import zipfile
import zlib
import struct
import olefile
import re
from tika import parser

class DOCExtractor:
    def __init__(self, filename):
        self._filename = filename
        self.text = self._get_text()

    def _get_text(self):
        parsed = parser.from_file(self._filename)
        return parsed['content'].strip() if parsed.get('content') else ""

    def get_text(self):
        return self.text

# HWPExtractor 클래스
class HWPExtractor:
    FILE_HEADER_SECTION = "FileHeader"
    HWP_SUMMARY_SECTION = "\x05HwpSummaryInformation"
    SECTION_NAME_LENGTH = len("Section")
    BODYTEXT_SECTION = "BodyText"
    HWP_TEXT_TAGS = [67]

    def __init__(self, filename):
        self._ole = self.load(filename)
        self._dirs = self._ole.listdir()

        self._valid = self.is_valid(self._dirs)
        if (self._valid == False):
            raise Exception("Not Valid HwpFile")
        
        self._compressed = self.is_compressed(self._ole)
        self.text = self._get_text()

    def load(self, filename):
        return olefile.OleFileIO(filename)

    def is_valid(self, dirs):
        if [self.FILE_HEADER_SECTION] not in dirs:
            return False

        return [self.HWP_SUMMARY_SECTION] in dirs

    def is_compressed(self, ole):
        header = self._ole.openstream("FileHeader")
        header_data = header.read()
        return (header_data[36] & 1) == 1

    def get_body_sections(self, dirs):
        m = []
        for d in dirs:
            if d[0] == self.BODYTEXT_SECTION:
                m.append(int(d[1][self.SECTION_NAME_LENGTH:]))

        return ["BodyText/Section"+str(x) for x in sorted(m)]

    def get_text(self):
        return self.text

    def _get_text(self):
        sections = self.get_body_sections(self._dirs)
        text = ""
        for section in sections:
            text += self.get_text_from_section(section)
            text += "\n"

        # 텍스트에서 한글, 영어, 숫자를 제외한 모든 문자 제거
        text = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)

        self.text = text
        return self.text

    def get_text_from_section(self, section):
        bodytext = self._ole.openstream(section)
        data = bodytext.read()

        unpacked_data = zlib.decompress(data, -15) if self.is_compressed else data
        size = len(unpacked_data)

        i = 0

        text = ""
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            level = (header >> 10) & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in self.HWP_TEXT_TAGS:
                rec_data = unpacked_data[i+4:i+4+rec_len]
                text += rec_data.decode('utf-16')
                text += "\n"

            i += 4 + rec_len

        return text
        

def get_text(filename):
    hwp = HWPExtractor(filename) 
    print(hwp.get_text())

class DOCXExtractor:
    NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = NAMESPACE + 'p'
    TEXT = NAMESPACE + 't'

    def __init__(self, filename):
        self._filename = filename
        self.text = self._get_text()

    def _get_text(self):
        document = zipfile.ZipFile(self._filename)
        xml_content = document.read('word/document.xml').decode()
        document.close()
        tree = ET.fromstring(xml_content)  # 수정: ET.fromstring 사용

        paragraphs = [
            ''.join([node.text for node in paragraph.findall('.//' + self.TEXT) if node.text])
            for paragraph in tree.findall('.//' + self.PARA)
        ]

        return '\n\n'.join(paragraphs)

    def get_text(self):
        return self.text


class PPTXExtractor:
    NAMESPACE = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
    TEXT = NAMESPACE + 't'
    SLIDE_PREFIX = "ppt/slides/slide"
    SLIDE_PREFIX_LENGTH = len(SLIDE_PREFIX)

    def __init__(self, filename):
        self._filename = filename
        self.text = self._get_text()

    def _get_text(self):
        document = zipfile.ZipFile(self._filename)
        slides = self._get_slide_names(document.namelist())
        texts = [self._extract_text_from_slide(document, slide) for slide in slides]
        document.close()
        return '\n'.join(texts)

    def _get_slide_names(self, dirs):
        return sorted(
            [d for d in dirs if d.startswith(self.SLIDE_PREFIX) and d.endswith('.xml')]
        )

    def _extract_text_from_slide(self, document, slide):
        xml_content = document.read(slide).decode()
        tree = ET.fromstring(xml_content)  # 수정: ET.fromstring 사용
        texts = [node.text for node in tree.findall('.//' + self.TEXT) if node.text]
        return '\n'.join(texts)

    def get_text(self):
        return self.text


def get_text(filename):
    pptx = PPTXExtractor(filename)
    print(pptx.get_text())

# XLSXExtractor 클래스
class XLSXExtractor:
    NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    TEXT = NAMESPACE + 't'
    SHARED_STRINGS = 'xl/sharedStrings.xml'

    def __init__(self, filename):
        self._filename = filename
        self.text = self._get_text()

    def _get_text(self):
        document = zipfile.ZipFile(self._filename)
        xml_content = document.read(self.SHARED_STRINGS).decode()
        document.close()
        tree = ET.fromstring(xml_content)  # 수정: ET.fromstring 사용
        texts = [node.text for node in tree.findall('.//' + self.TEXT) if node.text]
        return '\n'.join(texts)

    def get_text(self):
        return self.text


def get_text(filename):
    xlsx = XLSXExtractor(filename)
    print(xlsx.get_text())


# PDF에서 텍스트 추출을 위한 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        elif ext == ".pdf":
            images = convert_from_path(file_path)
            for image in images:
                text += pytesseract.image_to_string(image)
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
