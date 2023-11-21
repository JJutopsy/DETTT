import zipfile
import os

def extract_files(zip_path, output_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            encoded_file_name = file_info.filename
            
            # 파일 이름을 디코드해서 읽을 수 있는 형식으로 변환합니다.
            try:
                decoded_file_name = encoded_file_name.encode('cp437').decode('euc-kr', 'replace')
            except Exception as e:
                print(f"파일 이름을 디코드하는 중 오류가 발생했습니다: {e}")
                decoded_file_name = encoded_file_name

            print(f"파일 추출 중: {decoded_file_name}")

            # 지정된 디렉터리에 파일을 추출합니다.
            with zip_ref.open(encoded_file_name) as file:
                content = file.read()

                output_file_path = os.path.join(output_dir, decoded_file_name)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # 파일을 쓰기 모드(wb)로 열고 내용을 저장합니다.
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(content)

                print(f"파일이 여기로 추출되었습니다: {output_file_path}")

                # 추출한 파일이 또 다른 zip 파일인 경우, 이 함수를 재귀적으로 호출하여 내부 파일을 추출합니다.
                if decoded_file_name.lower().endswith('.zip'):
                    print("내부에 또 다른 zip 파일이 감지되었습니다. 추출 중...")
                    extract_files(output_file_path, os.path.join(output_dir, os.path.splitext(decoded_file_name)[0]))

if __name__ == "__main__":
    zip_path = input("ZIP 파일 경로를 입력하세요: ").strip()
    output_dir = "extracted_files"

    # 출력 디렉터리가 없으면 생성합니다.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ZIP 파일 경로가 올바른지와 실제로 존재하는지 확인합니다.
    if os.path.exists(zip_path) and zip_path.lower().endswith('.zip'):
        extract_files(zip_path, output_dir)
    else:
        print("올바른 ZIP 파일 경로를 입력하세요.")
