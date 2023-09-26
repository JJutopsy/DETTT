from tika import parser

class DocumentExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""

    def extract_content(self):
        parsed = parser.from_file(self.file_path)
        self.content = parsed['content'].strip()

    def save_to_file(self, output_file='extracted_combined.txt'):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.content)

    def get_content_as_list(self):
        # 텍스트를 줄바꿈 기준으로 나누어 리스트로 반환
        return self.content.splitlines()


# 모듈로 사용할 때 사용할 함수
def extract_content_from_file(file_path):
    extractor = DocumentExtractor(file_path)
    extractor.extract_content()
    return extractor.get_content_as_list()