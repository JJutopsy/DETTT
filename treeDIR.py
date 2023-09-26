import os
import sqlite3

# 검색할 디렉토리 경로 설정
start_dir = 'C:\\'  # 원하는 디렉토리 경로로 변경하세요.
full_path = os.path.dirname(start_dir)
# 찾을 확장자 리스트
extensions_to_find = ['.pdf', '.eml', '.docx', '.xlsx']

# SQLite3 데이터베이스 연결 및 테이블 생성
conn = sqlite3.connect('file_path.db')  # 데이터베이스 파일명을 수정하세요.
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS dirTest (file_path TEXT, full_path TEXT)')

# 디렉토리 탐색 함수 정의
def search_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 파일 확장자 확인
            _, file_extension = os.path.splitext(file_path)
            file_path = file_path[len(full_path)+1:]
            if file_extension.lower() in extensions_to_find:
                # 데이터베이스에 파일 경로 저장
                cursor.execute('INSERT INTO dirTest (file_path, full_path) VALUES (?, ?)', (file_path, full_path))
                conn.commit()
                print(f'파일: {file_path}')

# 디렉토리 탐색 시작
search_files(start_dir)

# 데이터베이스 연결 닫기
conn.close()
