import os
import pytsk3
import pyewf
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
parser = argparse.ArgumentParser(description="Process E01 image files.")
parser.add_argument('image_path', type=str, help="The path of the E01 image file to process.")
args = parser.parse_args()

# 원하는 확장자 목록
desired_extensions = [
    '.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt'
]

# DB 연결
conn = sqlite3.connect('parsing.sqlite')

# E01 파일을 처리하는 클래스
class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()

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
        logging.info("File data length: %d", len(file_data))  # 파일 데이터 길이 로깅
        
        ext = os.path.splitext(file_name)[1].lower()

        c_time, m_time, a_time = get_file_metadata(directory_entry)
        logging.info("File Metadata - Creation Time: %s, Modification Time: %s, Access Time: %s", c_time, m_time, a_time)

        file_text = parsing.extract_text(file_data, ext)  # 파일 텍스트 추출 로깅 제거
        
        hash_value = parsing.calculate_hash(file_data)  
        logging.info("Calculated hash: %s", hash_value)  # 계산된 해시 값 로깅

        blob_data = sqlite3.Binary(file_data)

        # file_info 변수의 일부 값만 로깅으로 확인
        file_info_log = (os.path.join(relative_path, file_name), hash_value, m_time.strftime("%Y-%m-%d %H:%M:%S"), a_time.strftime("%Y-%m-%d %H:%M:%S"), c_time.strftime("%Y-%m-%d %H:%M:%S"))
        file_info = (os.path.join(relative_path, file_name), hash_value, file_text, m_time.strftime("%Y-%m-%d %H:%M:%S"), a_time.strftime("%Y-%m-%d %H:%M:%S"), c_time.strftime("%Y-%m-%d %H:%M:%S"))
        logging.info("File info before saving to DB: %s", str(file_info_log))  # file_info 변수의 일부 값을 로깅으로 확인

        logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
        parsing.save_metadata_and_blob_to_db(conn, file_info, blob_data)
        logging.info("Data saved to DB: %s", file_info_log)  # DB에 데이터 저장 후 로깅

    except Exception as e:
        logging.exception("Exception occurred while processing the file: %s", file_name)







# 파일 메타데이터 추출 함수
def get_file_metadata(directory_entry):
    c_time = datetime.fromtimestamp(directory_entry.info.meta.crtime)
    m_time = datetime.fromtimestamp(directory_entry.info.meta.mtime)
    a_time = datetime.fromtimestamp(directory_entry.info.meta.atime)
    return c_time, m_time, a_time

# 메인 실행
try:
    # EWF 파일 핸들을 얻음
    filenames = pyewf.glob(args.image_path)
    ewf_handle = pyewf.handle()
    ewf_handle.open(filenames)

    # EWFImgInfo 인스턴스 생성
    ewf_img_info = EWFImgInfo(ewf_handle)
    logging.info("EWF Image Info created successfully.")

    # 파일 시스템을 직접 오픈
    fs_info = pytsk3.FS_Info(ewf_img_info)
    logging.info("File System Info obtained successfully.")

    # 디렉터리 순회
    directory = fs_info.open_dir(path="/")
    logging.info("Directory opened successfully.")
    process_directory(directory, fs_info, "")  # in_user_directory 파라미터 제거

    # 리소스 정리
    ewf_img_info.close()
    conn.close()  # DB 연결 종료
    logging.info("Completed.")

except Exception as e:
    logging.error(f"An error occurred: {e}")
