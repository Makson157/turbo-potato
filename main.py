import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.execute_query_and_fill_table(
            f"SELECT Coffee.id, Coffe.title, obgarka.title, Pomol.title, Coffe.opis,  "
            f"FROM coffee"
            f"INNER JOIN id_obg ON id_obg.id = Coffee.obgarka "
            f"INNER JOIN Pomol ON id_pom.id = coffee.Pomol;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())