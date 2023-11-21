from tika import parser

class DOCExtractor:
    def __init__(self, filename):
        self._filename = filename
        self.text = self._get_text()

    def _get_text(self):
        parsed = parser.from_file(self._filename)
        return parsed['content'].strip() if parsed.get('content') else ""

    def get_text(self):
        return self.text