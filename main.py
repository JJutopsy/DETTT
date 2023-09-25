import sys
from PyQt5 import uic
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QButtonGroup
from PyQt5.QtGui import QIcon

form_class = uic.loadUiType("./main.ui")[0]
newCase_class = uic.loadUiType("./newCase.ui")[0]
selectDrive_class = uic.loadUiType("./selectDrive.ui")[0]

class CaseSelectDialog(QDialog, selectDrive_class):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Case")
        self.setupUi(self)
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.drive_radio)
        self.radio_group.addButton(self.folder_radio)

        self.folder_input.setReadOnly(True)

        self.drive_radio.setChecked(True)
        self.folder_button.setEnabled(False)
        self.folder_input.setEnabled(False)
        self.populate_drive_list()
        self.drive_radio.toggled.connect(self.drive_radio_clicked)
        self.folder_radio.toggled.connect(self.folder_radio_clicked)
        self.folder_button.clicked.connect(self.select_folder)

    def populate_drive_list(self):
        drives = []
        for partition in psutil.disk_partitions():
            try:
                drive_name = f"{partition.device} {psutil.disk_usage(partition.mountpoint).total / (1024**3):.2f}GB"
                drives.append(drive_name)
            except OSError as e:
                print(f"Error reading drive: {e}")
    
        self.drive_combo.addItems(drives)
    def drive_radio_clicked(self):
        if self.drive_radio.isChecked():
            self.drive_combo.setEnabled(True)
            self.folder_input.setEnabled(False)
            self.folder_button.setEnabled(False)
        else:
            self.drive_combo.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.folder_input.setEnabled(True)

    def folder_radio_clicked(self):
        if self.folder_radio.isChecked():
            self.drive_combo.setEnabled(False)
    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.folder_input.setText(folder_path)
            

class CaseInputDialog(QDialog, newCase_class):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Case")


        self.setupUi(self)

        self.folder_button.clicked.connect(self.select_folder)
        self.folder_input.setReadOnly(True)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.case_name_input.textChanged.connect(self.check_inputs)

    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.folder_input.setText(folder_path)
            self.check_inputs()

    def check_inputs(self):
        case_name = self.case_name_input.text()
        folder_path = self.folder_input.text()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(bool(case_name) and bool(folder_path))

    def accept(self):
        super().accept()


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMinimumSize(800, 600)

        self.setWindowTitle('Demo v1')
        self.setWindowIcon(QIcon('./res/icon.png'))

        self.actionnew_2.triggered.connect(self.show_case_input_dialog)
        self.actionopen.triggered.connect(self.open_case_dialog)
    def show_case_input_dialog(self):
        case_input_dialog = CaseInputDialog()
        result = case_input_dialog.exec_()

        if result == QDialog.Accepted:
            case_name = case_input_dialog.case_name_input.text()
            folder_path = case_input_dialog.folder_input.text()
            print(f"Case Name: {case_name}")
            print(f"Selected Folder: {folder_path}")
            case_select_dialog = CaseSelectDialog()
            result = case_select_dialog.exec_()

    def open_case_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly 

        file_dialog = QFileDialog()
        file_name, _ = file_dialog.getOpenFileName(self, "Open File", "", "Text Files (*.case);;All Files (*)", options=options)

        if file_name:
            print("Selected file path:", file_name)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()

    myWindow.show()
    app.exec_()
