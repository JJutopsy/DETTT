import zipfile
import xml.etree.ElementTree as ET

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path

    def _parse_word_xml(self):
        # 결과를 저장할 리스트
        result_list = []

        # .docx 파일을 zip으로 열기
        with zipfile.ZipFile(self.docx_path, 'r') as z:
            # word/document.xml 추출
            with z.open('word/document.xml') as f:
                # XML 파싱
                tree = ET.parse(f)
                root = tree.getroot()

                # 'w:t' 태그가 있는 모든 요소를 찾아 텍스트 추출
                for elem in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    result_list.append(elem.text)

        return result_list

    def get_plain_texts(self):
        return self._parse_word_xml()
