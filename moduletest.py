import modules.docx_parser
import modules.doc_parser
import modules.google_EMLParser


docx = modules.docx_parser.DocxParser("C:\\Users\\dswhd\\OneDrive\\문서\\카카오톡 받은 파일\\aaa.docx")
print(docx.get_plain_texts())

print("-"*30)

doc = modules.doc_parser.extract_content_from_file("C:\\Users\\dswhd\\OneDrive\\문서\\디포 자료\\행복의류 증거데이터 v0811\\구매팀_강수민(대리)\\C\\HB_sumin\\Downloads\\업무관련 서식\\업무관련 서식\\회계전표\\회계전표.doc")
print(doc)

