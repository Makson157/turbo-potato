import sqlite3
import sys
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLabel, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt
# импорт всего что нужно и не очень


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('1.ui', self)
        self.params = {}
        self.con = sqlite3.connect("../../Desktop/pythonProject1/pesni.sqlite")
        self.select_genres()
        self.queryButton.clicked.connect(self.select)
        self.setWindowTitle('Фильтрация по жанрам')
        self.execute_query_and_fill_table(
            f"SELECT Pesnya.id, Pesnya.Nazvanie, Genres.Nazvanie, Pesnya.Year, Ispolniteli.Name "
            f"FROM Pesnya "
            f"INNER JOIN Genres ON Genres.id = Pesnya.Genre "
            f"INNER JOIN Ispolniteli ON Ispolniteli.id = Pesnya.Ispolnitel")
        self.vibor = False
        self.pushButton.clicked.connect(self.show_window)
        self.tableWidget.cellClicked.connect(self.current_row)
        self.pushButton_2.clicked.connect(self.new_item)

    # переход в 3 окно
    def new_item(self):
        self.wind = New()
        self.wind.show()

    def current_row(self, event):
        row = self.tableWidget.currentRow()
        value = self.tableWidget.item(row, 0).text()
        # получил id строки из БД
        cur = self.con.cursor()
        self.vibor = cur.execute("SELECT id FROM Pesnya WHERE id=?", (value,)).fetchone()

    # переход во второе окно
    def show_window(self):
        if self.vibor:
            self.new_window = Info(self.vibor)
            self.new_window.show()
        else:
            # ошибка, если не выбрали песню, а информацию запросили
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Не выбрана песня из таблицы')
            msg.setWindowTitle("Error")
            msg.exec_()

    def select_genres(self):
        req = "SELECT * from genres"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall():
            self.params[key] = value
        self.parameterSelection.addItems(list(self.params.keys()))

    def select(self):
        cur = self.con.cursor()
        janr = self.parameterSelection.currentText()
        idj = cur.execute(f"SELECT id FROM Genres WHERE Nazvanie = '{janr}'").fetchone()[0]
        req = (f"SELECT Pesnya.id, Pesnya.Nazvanie, Genres.Nazvanie, Pesnya.Year, Ispolniteli.Name FROM Pesnya "
               f"INNER JOIN Genres ON Genres.id = Pesnya.Genre "
               f"INNER JOIN Ispolniteli ON Ispolniteli.id = Pesnya.Ispolnitel "
               f"WHERE Genre = {idj}")
        self.execute_query_and_fill_table(req)

    def execute_query_and_fill_table(self, query):
        cur = self.con.cursor()
        result = cur.execute(query).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(["№", "Название", "Жанр", "Год", 'Исполнитель'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def closeEvent(self, event):
        self.con.close()


class Info(QMainWindow):
    def __init__(self, row):
        super().__init__()
        uic.loadUi("INFO.ui", self)
        self.row = row[0]
        self.con = sqlite3.connect("../../Desktop/pythonProject1/pesni.sqlite")
        self.item_changed()
        self.pushButton.clicked.connect(self.play)
        self.pushButton_2.clicked.connect(self.close)
        self.modified = {}
        self.titles = None
        self.media_play = False

    # метод проигрывания файлов
    def play(self):
        # создали плеер
        self.media = QMediaPlayer()
        cur = self.con.cursor()
        url = QUrl.fromLocalFile(cur.execute('SELECT Music FROM Pesnya WHERE id=?', (self.row,)).fetchone()[0])
        # преобразовали в нужный формат
        content = QMediaContent(url)
        # передали файл в плеер
        self.media.setMedia(content)
        # проигрываем файл
        self.media.play()
        # поставили флаг включенного плеера
        self.media_play = True

    # метод остановки прогигрывания файлов
    def close(self):
        # проверили включен ли плеер
        if self.media_play:
            # выключили плеер
            self.media.stop()
            # опутсили флаг включенного плеера
            self.media_play = False

    # выбираем элементы  по переданному id
    def item_changed(self):
        self.lineEdit_5.setText(f'{self.row}')
        cur = self.con.cursor()
        self.result = cur.execute(f"SELECT Pesnya.id, Pesnya.Nazvanie, Genres.Nazvanie, Pesnya.Year, Ispolniteli.Name "
                                  f"FROM Pesnya "
                                  f"LEFT JOIN Genres ON Genres.id = Pesnya.Genre "
                                  f"LEFT JOIN Ispolniteli ON Ispolniteli.id = Pesnya.Ispolnitel "
                                  f"WHERE Pesnya.id = {self.row}").fetchone()
        self.save_results()

    def save_results(self):
        # тут передаю всё во второе окно
        self.lineEdit_5.setText(str(self.result[0]))
        self.lineEdit.setText(str(self.result[1]))
        self.lineEdit_2.setText(str(self.result[2]))
        self.lineEdit_3.setText(str(self.result[3]))
        self.lineEdit_4.setText(str(self.result[4]))
        cur = self.con.cursor()
        data_img = cur.execute('''SELECT Image FROM Pesnya WHERE id =?''', (self.result[0],)).fetchone()
        self.image.setPixmap(QPixmap(data_img[0]))

    # метод закрытия подключения к БД в момент закрытия окна (есть во всех классах)
    def closeEvent(self, event):
        self.con.close()


class New(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Dobavit.ui', self)
        self.con = sqlite3.connect('../../Desktop/pythonProject1/pesni.sqlite')
        self.cur = self.con.cursor()
        self.pushButton.clicked.connect(self.dob_pes)
        self.pushButton_2.clicked.connect(self.dob_kar)
        self.pushButton_3.clicked.connect(self.save_izm)

    def dob_pes(self):
        # np = novaya pesnya
        np = QFileDialog.getOpenFileName(
            self, 'Выбрать песню', '',
            'Песня (*.mp3);;Все файлы (*)')[0]
        # тоже самое что и ниже

    def dob_kar(self):
        # nk = новая картинка
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        QImage.save(fname) # плохо понял, в интернете не нашёл

    def save_izm(self):
        pass


        # TODO пользователь заполняет информацию в полях, если он нажал добавить картинку
        #  выплывает окно открытия картинки (урок QT 5 п.2) и мы сохраняем картинку в папку img;
        #  если он нажал добавить музыку мы поступаем аналогично картинке;
        #  если он нажал СОХРАНИТЬ мы проверяем введенную информацию (год не слишком большой и не слишком маленький
        #  и т.п.) и в случае проблем выводим сообщение об ошибке в QMessageBox, в противном случае отправляем
        #  данные в БД

    def select_genres(self):
        req = "SELECT * from genres"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall():
            self.params[key] = value
        self.parameterSelection1.addItems(list(self.params.keys()))

    def select_ispolnitel(self):
        req = "SELECT * from ispolniteli"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall():
            self.params[key] = value
        self.parameterSelection2.addItems(list(self.params.keys()))

    def closeEvent(self, event):
        self.con.close()


# отлавливаем ошибку
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# для вызова программы
if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = Main()
    ex.show()
    sys.exit(app.exec())
