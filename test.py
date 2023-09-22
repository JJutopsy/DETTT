import sys
import psutil
from PyQt5.QtWidgets import QApplication, QDialog, QComboBox, QVBoxLayout, QPushButton, QRadioButton, QButtonGroup, QFileDialog

class DriveSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Drive/Folder Selection")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.drive_radio = QRadioButton("Drive Selection")
        self.folder_radio = QRadioButton("Folder Selection")

        # 라디오 버튼 그룹을 생성하여 하나만 선택 가능하도록 설정
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.drive_radio)
        self.radio_group.addButton(self.folder_radio)
        self.folder_radio.setChecked(True)

        self.drive_combo = QComboBox()
        self.drive_combo.setEnabled(False)

        self.populate_drive_list()
        
        layout.addWidget(self.drive_radio)
        layout.addWidget(self.folder_radio)
        layout.addWidget(self.drive_combo)

        select_button = QPushButton("Select Drive/Folder")
        select_button.clicked.connect(self.select_drive_or_folder)
        layout.addWidget(select_button)

        self.setLayout(layout)

        self.drive_radio.toggled.connect(self.drive_radio_clicked)
        self.folder_radio.toggled.connect(self.folder_radio_clicked)

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
        else:
            self.drive_combo.setEnabled(False)

    def folder_radio_clicked(self):
        if self.folder_radio.isChecked():
            self.drive_combo.setEnabled(False)

    def select_drive_or_folder(self):
        if self.drive_radio.isChecked():
            selected_drive = self.drive_combo.currentText()
            print(f"Selected drive: {selected_drive}")
        elif self.folder_radio.isChecked():
            folder_dialog = QFileDialog()
            folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

            if folder_path:
                print(f"Selected folder: {folder_path}")
        else:
            print("Please select either 'Drive Selection' or 'Folder Selection'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DriveSelectionDialog()
    result = dialog.exec_()

    if result == QDialog.Accepted:
        sys.exit(0)
    else:
        sys.exit(1)
