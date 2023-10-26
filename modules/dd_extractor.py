import os
import pytsk3
import logging
import sys
import sqlite3
import argparse
import parsing
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 명령 줄 인수 처리
parser = argparse.ArgumentParser(description="Process DD or RAW image files.")
parser.add_argument('image_path', type=str, help="The path of the DD or RAW image file to process.")
args = parser.parse_args()

# 원하는 확장자 목록
desired_extensions = [
    '.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv','txt']

# DB 연결
conn = sqlite3.connect('parsing.sqlite')

# 디렉터리 처리 함수
def process_directory(directory, fs_info, relative_path, in_user_directory=False):
    for directory_entry in directory:
        try:
            if directory_entry.info.meta is None:
                continue

            if directory_entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                sub_directory = directory_entry.as_directory()
                sub_directory_name = directory_entry.info.name.name.decode()

                if sub_directory_name not in ['.', '..']:
                    path = os.path.join(relative_path, sub_directory_name)
                    logging.info(f"Processing directory: {path}, In user directory: {in_user_directory}")

                    if sub_directory_name.lower() in ['users', '사용자']:
                        process_directory(sub_directory, fs_info, path, True)
                    else:
                        process_directory(sub_directory, fs_info, path, in_user_directory)

            elif directory_entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG and in_user_directory:
                file_name = directory_entry.info.name.name.decode()
                _, ext = os.path.splitext(file_name)
                
                logging.info(f"Checking file: {os.path.join(relative_path, file_name)} with extension {ext}")

                if ext.lower() in desired_extensions:
                    logging.info(f"Found file: {os.path.join(relative_path, file_name)}")
                    extract_file(directory_entry, fs_info, file_name, relative_path)

        except Exception as e:
            logging.error(f"Error occurred while processing directory: {e}")
            continue

# 파일 추출 함수
def extract_file(directory_entry, fs_info, file_name, relative_path):
    try:
        file_object = fs_info.open_meta(inode=directory_entry.info.meta.addr)
        file_data = file_object.read_random(0, file_object.info.meta.size)
        ext = os.path.splitext(file_name)[1].lower()

        c_time, m_time, a_time = get_file_metadata(directory_entry)
        logging.info("File Metadata - Creation Time: %s, Modification Time: %s, Access Time: %s", c_time, m_time, a_time)

        file_text = parsing.extract_text(file_data, ext)  
        hash_value = parsing.calculate_hash(file_data)  # parsing.calculate_hash 함수를 직접 호출

        blob_data = sqlite3.Binary(file_data)  

        file_info = (os.path.join(relative_path, file_name), hash_value, file_text, str(m_time), str(a_time), str(c_time))
        parsing.save_metadata_and_blob_to_db(conn, file_info, blob_data)
        logging.info("Data saved to DB: %s", file_info[:6])  


    except Exception as e:
        logging.error("Failed to extract or save data for file: %s", file_name)


# 파일 메타데이터 추출 함수
def get_file_metadata(directory_entry):
    c_time = datetime.fromtimestamp(directory_entry.info.meta.crtime)
    m_time = datetime.fromtimestamp(directory_entry.info.meta.mtime)
    a_time = datetime.fromtimestamp(directory_entry.info.meta.atime)
    return c_time, m_time, a_time

# 메인 실행
try:
    img_info = pytsk3.Img_Info(args.image_path)
    logging.info("RAW Image Info created successfully.")

    fs_info = pytsk3.FS_Info(img_info)
    logging.info("File System Info obtained successfully.")

    directory = fs_info.open_dir(path="/")
    logging.info("Directory opened successfully.")

    process_directory(directory, fs_info, "")  # 수정된 부분
    logging.info("Completed.")
    
    conn.close()  # DB 연결 종료 추가된 부분
    logging.info("Database connection closed.")

except Exception as e:
    logging.error("An error occurred: %s", e)
    logging.error("Details: %s", e.args)  # 예외 처리 세부 정보 추가
