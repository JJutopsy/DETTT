import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon

form_class = uic.loadUiType("./main.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMinimumSize(800, 600)

        self.setWindowTitle('문서이메일탈탈털기툴')
        self.setWindowIcon(QIcon('./res/icon.png'))

        self.actionopen.triggered.connect(self.open_file_dialog)
        self.actionnew_2.triggered.connect(self.select_folder)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # 읽기 전용으로 파일 열기

        file_dialog = QFileDialog()
        file_name, _ = file_dialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            print("Selected file path:", file_name)

    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            print("Selected folder path:", folder_path)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()

    myWindow.show()
    app.exec_()
