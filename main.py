import sys
from PyQt5 import uic
from random import randint
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Ui.ui, self')
        self.flag = False
        self.pushButton.clicked.connect(self.go_paint)

    def go_paint(self):
        self.qp = QPainter()
        self.flag = True
        self.update()



    def paintEvent(self, event):
        if self.flag:
            self.qp.begin(self)
            self.draw_flag(self.qp)
            self.qp.end()

    def draw_flag(self, qp):
        qp.setBrush(QColor(255, 255, 0))
        # Рисуем прямоугольник заданной кистью
        x, y = randint(0, 316), randint(0, 267)
        d = randint(10, 30)
        self.qp.drawEllipse(x, y, d, d)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())