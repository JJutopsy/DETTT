import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
class FileTreeView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File TreeView Example')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.treeView = QTreeView()
        layout.addWidget(self.treeView)
        
        self.conn = sqlite3.connect('files.sqlite')  
        self.cursor = self.conn.cursor()
        

        self.cursor.execute('SELECT file_path FROM dirTest')
        
        self.model = QStandardItemModel()
        self.populate_treeview()
 
        self.treeView.setModel(self.model)

    def populate_treeview(self):
        for row in self.cursor.fetchall():
            file_path = row[0]  
           
            self.add_path_to_treeview(file_path)

    def add_path_to_treeview(self, path):
        root = self.model.invisibleRootItem()
        path_parts = path.split("\\")  # 파일 경로를 경로 부분으로 분할

        # TreeView에 경로를 추가
        current_item = root
        for part in path_parts:
            child_item = None
            for row in range(current_item.rowCount()):
                child = current_item.child(row)
                if child.text() == part:
                    
                    child_item = child
                    break
            if not child_item:
                child_item = QStandardItem(part)
                current_item.appendRow(child_item)
            current_item = child_item
            # 아이템을 읽기 전용으로 설정
            child_item.setFlags(child_item.flags() & ~Qt.ItemIsEditable)


def main():
    app = QApplication(sys.argv)
    window = FileTreeView()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
