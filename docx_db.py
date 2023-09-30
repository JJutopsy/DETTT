import os
import sqlite3
import hashlib
import time
from modules.docx_parser import DocxParser  # 모듈에서 필요한 클래스 가져오기

# 검색할 디렉토리 경로 설정
start_dir = 'C:\\Users\\dswhd\\OneDrive\\문서\\디포 자료\\행복의류 증거데이터 v0811'  # 원하는 디렉토리 경로로 변경하세요.

# SQLite3 데이터베이스 연결 및 테이블 생성 (sha256 열 추가)
conn = sqlite3.connect('docx_files.sqlite')  # 데이터베이스 파일명을 수정하세요.
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS dirTest (file_path TEXT, plain_text TEXT, sha256 TEXT, created_time INTEGER, modified_time INTEGER, accessed_time INTEGER)')

# 디렉토리 탐색 함수 정의
def search_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 파일 확장자 확인
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() in extensions_to_find:
                # SHA-256 해시 계산
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    # 파일을 작은 덩어리로 나눠서 읽어들여 해시 계산
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                sha256 = sha256_hash.hexdigest()

                # 파일 정보 얻기 (생성 시간, 수정된 시간, 접근 시간)
                created_time = os.path.getctime(file_path)
                modified_time = os.path.getmtime(file_path)
                accessed_time = os.path.getatime(file_path)
                docx = DocxParser(file_path)  # 모듈에서 가져온 클래스 사용
                plain_text = ""
                for i in docx.get_plain_texts():
                    plain_text += i

                # 데이터베이스에 파일 정보 저장
                cursor.execute('INSERT INTO dirTest (file_path, plain_text, sha256, created_time, modified_time, accessed_time) VALUES (?, ?, ?, ?, ?, ?)', (file_path, plain_text, sha256, created_time, modified_time, accessed_time))
                conn.commit()
                print(f'파일: {file_path}')

# 찾을 확장자 리스트
extensions_to_find = ['.docx']

# 디렉토리 탐색 시작
search_files(start_dir)

# 데이터베이스 연결 닫기
conn.close()
