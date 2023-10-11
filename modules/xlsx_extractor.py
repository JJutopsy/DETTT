import xml.etree.ElementTree as ET
import zipfile

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