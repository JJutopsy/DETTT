import modules.docx_parser

docx = modules.docx_parser.DocxParser("C:\\Users\\SeoJongChan\\Documents\\카카오톡 받은 파일\\aaa.docx")
print(*docx.get_plain_texts())