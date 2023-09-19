import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

form_class = uic.loadUiType("./main.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('문서이메일탈탈털기툴')
        self.setWindowIcon(QIcon('icon.png'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    
    myWindow.show()
    app.exec_()