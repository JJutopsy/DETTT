import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Table Viewer")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # SQLite 데이터베이스 연결
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("./db/cases.sqlite") 
        if not self.db.open():
            print("Database connection failed")
            sys.exit(1)

        # QSqlTableModel 설정
        self.model = QSqlTableModel()
        self.model.setTable("cases")  # 테이블명을 수정하세요.
        self.model.select()

        # 테이블 뷰 생성 및 모델 설정
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # 레이아웃에 테이블 뷰 추가
        self.layout.addWidget(self.table_view)

def main():
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
