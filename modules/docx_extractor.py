import xml.etree.ElementTree as ET
import zipfile

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