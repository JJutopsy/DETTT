import xml.etree.ElementTree as ET
import zipfile

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
