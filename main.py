import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.QtGui import QIcon

form_class = uic.loadUiType("./main.ui")[0]

class CaseInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Case")

        layout = QVBoxLayout()

        self.case_name_label = QLabel("Case Name:")
        self.case_name_input = QLineEdit()

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)

        self.folder_input = QLineEdit()  # 폴더 경로를 표시할 QLineEdit 추가
        self.folder_input.setReadOnly(True)  # 읽기 전용으로 설정

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)  # 처음에는 비활성화

        layout.addWidget(self.case_name_label)
        layout.addWidget(self.case_name_input)
        layout.addWidget(self.folder_button)
        layout.addWidget(self.folder_input)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # 텍스트 입력 필드가 변경될 때마다 체크
        self.case_name_input.textChanged.connect(self.check_inputs)

    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.folder_input.setText(folder_path)
            self.check_inputs()

    def check_inputs(self):
        # 두 입력 필드 모두 값이 있을 때 "OK" 버튼 활성화
        case_name = self.case_name_input.text()
        folder_path = self.folder_input.text()
        self.ok_button.setEnabled(bool(case_name) and bool(folder_path))

    def accept(self):
        super().accept()


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMinimumSize(800, 600)

        self.setWindowTitle('문서이메일탈탈털기툴')
        self.setWindowIcon(QIcon('./res/icon.png'))

        # "actionnew_2" 메뉴 아이템에 대한 클릭 이벤트 핸들러 연결
        self.actionnew_2.triggered.connect(self.show_case_input_dialog)

    def show_case_input_dialog(self):
        case_input_dialog = CaseInputDialog()
        result = case_input_dialog.exec_()

        if result == QDialog.Accepted:
            case_name = case_input_dialog.case_name_input.text()
            folder_path = case_input_dialog.folder_input.text()
            print(f"Case Name: {case_name}")
            print(f"Selected Folder: {folder_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()

    myWindow.show()
    app.exec_()
