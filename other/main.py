import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction
from PyQt5.QtWidgets import QCalendarWidget, QLabel, QPushButton, QPlainTextEdit, QFileDialog
from PyQt5.QtCore import QDate
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import sqlite3
import xlsxwriter
import datetime


MONTH = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
         'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


# Класс отвечающий за главное окно
class Window(QMainWindow):
    """The class responsible for the main window"""

    def __init__(self):
        """initializer function"""
        super(Window, self).__init__()
        uic.loadUi('main_window.ui', self)
        self.setWindowTitle('Счётчик рассходов')

        # создание базы данных
        self.database = sqlite3.connect('count_info.sqlite')
        cur = self.database.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS
                    standart_outgo(dayid INT PRIMARY KEY, outgo INT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS 
                    plan_outgo(dayid INT PRIMARY KEY, outgo INT)""")

        self.unitUI()

    # Функция, которая отвечает за привязку кнопок к функциям
    def unitUI(self):
        """A function that is responsible for binding buttons to functions"""
        # Создание действий и добавление их на menuBar
        self.action_info = QAction('О программе', self)
        self.action_info.triggered.connect(self.info)
        self.menu.addAction(self.action_info)

        self.action_excel_otp = QAction('Вывод в Excel', self)
        self.action_excel_otp.triggered.connect(self.excel_output)
        self.menuExcel.addAction(self.action_excel_otp)

        # Привязка функций к кнопкам
        self.input_stand_outgo.clicked.connect(self.add_outgo)
        self.input_plan_outgo.clicked.connect(self.add_plan)
        self.del_stan_outgo.clicked.connect(self.del_outgo)
        self.del_plan_outgo.clicked.connect(self.del_plan)
        self.return_stand_graph.clicked.connect(self.return_only_outgo_graph)
        self.return_plan_graph.clicked.connect(self.return_only_plan_graph)
        self.return_both_graph.clicked.\
            connect(self.return_outgo_and_plan_graph)

    # Функция, которая отвечает за вывод информации из базы данных в xlsx формат
    def excel_output(self):
        """The function that is responsible for displaying information from the database in xlsx format"""
        # Создание excel файла
        workbook = xlsxwriter.Workbook('Output.xlsx')
        worksheet = workbook.add_worksheet()
        std = workbook.add_format({'bg_color': '#ff4940'})
        pln = workbook.add_format({'bg_color': '00ffff'})
        worksheet.merge_range('A1:B1', 'Обязательные траты', std)
        worksheet.merge_range('C1:D1', 'Планируемые траты', pln)

        cur = self.database.cursor()
        # получение данных по обязательным тратам
        command = "SELECT * FROM standart_outgo ORDER BY dayid"
        data = cur.execute(command).fetchall()
        dates = []
        month_num = ['01', '03', '05', '07', '08', '10', '12']
        now = datetime.datetime.now().strftime('%m')
        year = int(datetime.datetime.now().strftime('%y'))
        for date in data:
            dates.append(date[0])
        if now in month_num:
            num = 32
        elif now not in month_num and now != '02':
            num = 31
        elif now == '02' and year % 4 == 0:
            if not (year % 100 == 0 and year % 400 != 0):
                num = 30
            else:
                num = 29
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data.append((i, 0))
        data = sorted(data, key=lambda x: x[0])
        # внесение данных по стандартным тратам в excel
        for row, (date, outgo) in enumerate(data):
            worksheet.write(row + 1, 0,
                            f'{date}.'
                            f'{datetime.datetime.now().strftime("%m")}',
                            std)
            worksheet.write(row + 1, 1, outgo, std)
        # Получение данных по планируемым тратам
        command = "SELECT * FROM plan_outgo ORDER BY dayid"
        data = cur.execute(command).fetchall()
        dates = []
        for date in data:
            dates.append(date[0])
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data.append((i, 0))
        data = sorted(data, key=lambda x: x[0])
        # внесение данных по планируемым тратам в excel
        for row, (date, outgo) in enumerate(data):
            worksheet.write(row + 1, 2,
                            f'{date}.'
                            f'{datetime.datetime.now().strftime("%m")}',
                            pln)
            worksheet.write(row + 1, 3, outgo, pln)
        workbook.close()

    # Функция, которая создаёт окно класса InfoWindow
    def info(self):
        """A function that creates a window of the InfoWindow class"""
        self.wnd1 = InfoWindow()
        self.wnd1.show()

    # Функция, которая создаёт окно класса Input_Window, которое будет отвечать за ввод обязательных трат
    def add_outgo(self):
        """A function that creates a window of class Input_Window for standart outgo"""
        self.wnd1 = Input_Window('standart', self.database)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Input_Window, которое будет отвечать за ввод планируемых трат
    def add_plan(self):
        """A function that creates a window of class Input_Window for plan outgo"""
        self.wnd1 = Input_Window('plan', self.database)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Del_Window, которое будет отвечать за удаление обязательных трат
    def del_outgo(self):
        """A function that creates a window of class Del_Window for standart outgo"""
        self.wnd1 = Del_Window('standart', self.database)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Del_Window, которое будет отвечать за удаление планируемых трат
    def del_plan(self):
        """A function that creates a window of class Del_Window for plan outgo"""
        self.wnd1 = Del_Window('plan', self.database)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Output_Window, которое отвечает за вывод графика по обязательным тратам
    def return_only_outgo_graph(self):
        """A function that creates a graph for standart outgo, and then creates a window of class Output_Window"""
        # Создание графика
        cur = self.database.cursor()
        command = "SELECT * FROM standart_outgo ORDER BY dayid"
        data = cur.execute(command).fetchall()
        dates = []
        month_num = ['01', '03', '05', '07', '08', '10', '12']
        now = datetime.datetime.now().strftime('%m')
        year = int(datetime.datetime.now().strftime('%y'))
        for date in data:
            dates.append(date[0])
        if now in month_num:
            num = 32
        elif now not in month_num and now != '02':
            num = 31
        elif now == '02' and year % 4 == 0:
            if not (year % 100 == 0 and year % 400 != 0):
                num = 30
            else:
                num = 29
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data.append((i, 0))
        data = sorted(data, key=lambda x: x[0])
        x = []
        y = []
        for date in data:
            x.append(date[0])
            y.append(date[1])
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_facecolor('seashell')
        plt.title('Данные о обязательных тратах')
        mth = MONTH[int(datetime.datetime.now().strftime("%m")) - 1]
        plt.xlabel(f'Дата, {mth}')
        plt.ylabel('Трата, рубли')
        plt.grid(True)
        # Сохранение графика как png изображение
        plt.savefig('output')
        # Создание окна
        self.wnd1 = Output_Window('output.png', data)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Output_Window, которое отвечает за вывод графика по планируемым тратам
    def return_only_plan_graph(self):
        """A function that creates a graph for plan outgo, and then creates a window of class Output_Window"""
        # Создание графика
        cur = self.database.cursor()
        command = "SELECT * FROM plan_outgo ORDER BY dayid"
        data = cur.execute(command).fetchall()
        dates = []
        month_num = ['01', '03', '05', '07', '08', '10', '12']
        now = datetime.datetime.now().strftime('%m')
        year = int(datetime.datetime.now().strftime('%y'))
        for date in data:
            dates.append(date[0])
        if now in month_num:
            num = 32
        elif now not in month_num and now != '02':
            num = 31
        elif now == '02' and year % 4 == 0:
            if not (year % 100 == 0 and year % 400 != 0):
                num = 30
            else:
                num = 29
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data.append((i, 0))
        data = sorted(data, key=lambda x: x[0])
        x = []
        y = []
        for date in data:
            x.append(date[0])
            y.append(date[1])
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_facecolor('seashell')
        plt.title('Данные о планируемых тратах')
        mth = MONTH[int(datetime.datetime.now().strftime("%m")) - 1]
        plt.xlabel(f'Дата, {mth}')
        plt.ylabel('Трата, рубли')
        plt.grid(True)
        # Сохранение графика как png изображение
        plt.savefig('output')
        # Создание окна
        self.wnd1 = Output_Window('output.png', data)
        self.wnd1.show()

    # Функция, которая создаёт окно класса Output_Window, которое отвечает за вывод графика по всем тратам
    def return_outgo_and_plan_graph(self):
        """
        A function that creates a graph for standart and
        plan outgo, and then creates a window of class Output_Window
        """
        # Создание графика
        cur = self.database.cursor()
        command = "SELECT * FROM standart_outgo ORDER BY dayid"
        data = cur.execute(command).fetchall()
        command2 = "SELECT * FROM plan_outgo ORDER BY dayid"
        data2 = cur.execute(command2).fetchall()
        dates = []
        month_num = ['01', '03', '05', '07', '08', '10', '12']
        now = datetime.datetime.now().strftime('%m')
        year = int(datetime.datetime.now().strftime('%y'))
        for date in data:
            dates.append(date[0])
        if now in month_num:
            num = 32
        elif now not in month_num and now != '02':
            num = 31
        elif now == '02' and year % 4 == 0:
            if not (year % 100 == 0 and year % 400 != 0):
                num = 30
            else:
                num = 29
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data.append((i, 0))
        data = sorted(data, key=lambda x: x[0])
        dates = []
        for date in data2:
            dates.append(date[0])
        for i in range(1, num):
            if i in dates:
                continue
            else:
                data2.append((i, 0))
        data2 = sorted(data2, key=lambda x: x[0])
        data_out = []
        for i in range(1, num):
            data_out.append((i, data[i - 1][1] + data2[i - 1][1]))
        x = []
        y = []
        for date in data_out:
            x.append(date[0])
            y.append(date[1])
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_facecolor('seashell')
        plt.title('Данные о тратах')
        mth = MONTH[int(datetime.datetime.now().strftime("%m")) - 1]
        plt.xlabel(f'Дата, {mth}')
        plt.ylabel('Трата, рубли')
        plt.grid(True)
        # Сохранение графика как png изображение
        plt.savefig('output')
        # Создание окна
        self.wnd1 = Output_Window('output.png', data_out)
        self.wnd1.show()


# Класс отвечающий за окно ввода данных
class Input_Window(QWidget):
    """The class responsible for the input window"""

    def __init__(self, table, db):
        """initializer function, accepts table type information and database"""
        super(Input_Window, self).__init__()
        uic.loadUi('input_window.ui', self)

        self.table_name = table
        self.database = db
        self.setWindowTitle('Ввод данных')

        self.calendarWidget.setNavigationBarVisible(False)
        self.calendarWidget.setVerticalHeaderFormat(0)

        month = self.calendarWidget.monthShown()
        year = self.calendarWidget.yearShown()
        date = QDate(year, month, 1)
        self.calendarWidget.setMinimumDate(date)
        if month in [1, 3, 5, 7, 8, 10, 12]:
            date = QDate(year, month, 31)
        elif month == 2 and year % 4:
            if not (year % 100 == 0 and year % 400 != 0):
                date = QDate(year, month, 29)
            else:
                date = QDate(year, month, 28)
        else:
            date = QDate(year, month, 30)
        self.calendarWidget.setMaximumDate(date)
        self.label_2.setText(MONTH[int(month - 1)])
        self.calendarWidget.clicked['QDate'].connect(self.add_data)

    # Функция, которая вносит данные в базу данных
    def add_data(self, date):
        """A function that inserts data into a database"""
        date = int(date.toString('dd'))
        # Вносит информацию в таблицу базы данных standart_outgo
        if self.table_name == 'standart':

            if self.data_input.text().isdigit():
                cur = self.database.cursor()
                outgo = self.data_input.text()
                is_into = cur.execute(f"""SELECT * FROM standart_outgo
                                      WHERE dayid = {date}""")
                if is_into.fetchone() == None:
                    cur.execute(f"""INSERT INTO standart_outgo 
                                VALUES({date}, {outgo})""")
                    self.database.commit()
                else:
                    cur.execute(f"""UPDATE standart_outgo SET outgo =
                                outgo + {outgo} WHERE dayid = {date}""")
                    self.database.commit()

                self.label.setText('Данные внесены')

            else:
                self.label.setText('Непраильный формат ввода')

        # Вносит информацию в таблицу базы данных plan_outgo
        elif self.table_name == 'plan':

            if self.data_input.text() and self.data_input.text().isdigit():
                cur = self.database.cursor()
                outgo = self.data_input.text()
                is_into = cur.execute(f"""SELECT * FROM plan_outgo
                                      WHERE dayid = {date}""")
                if is_into.fetchone() == None:
                    cur.execute(f"""INSERT INTO plan_outgo
                                VALUES({date}, {outgo})""")
                    self.database.commit()
                else:
                    cur.execute(f"""UPDATE plan_outgo SET outgo =
                                outgo + {outgo} WHERE dayid = {date}""")
                    self.database.commit()

                self.label.setText('Данные внесены')

            else:
                self.label.setText('Непраильный формат ввода')


# Класс отвечающий за окно удаления данных
class Del_Window(QWidget):
    """The class responsible for the delete window"""

    def __init__(self, table, db):
        """initializer function, accepts table type information and database"""
        super(Del_Window, self).__init__()
        uic.loadUi('del_window.ui', self)

        self.table_name = table
        self.databse = db
        self.setWindowTitle('Удаление данных')

        self.calendarWidget.setNavigationBarVisible(False)
        self.calendarWidget.setVerticalHeaderFormat(0)

        month = self.calendarWidget.monthShown()
        year = self.calendarWidget.yearShown()
        date = QDate(year, month, 1)
        self.calendarWidget.setMinimumDate(date)
        if month in [1, 3, 5, 7, 8, 10, 12]:
            date = QDate(year, self.month, 31)
        elif month == 2 and year % 4 == 0:
            if not (month % 100 == 0 and month % 400 != 0):
                date = QDate(year, month, 29)
            else:
                date = QDate(year, month, 28)
        else:
            date = QDate(year, month, 30)
        self.calendarWidget.setMaximumDate(date)
        self.label_2.setText(MONTH[int(month - 1)])
        self.calendarWidget.clicked['QDate'].connect(self.del_data)

    # Функция, которая отвеает за удаление данных
    def del_data(self, date):
        """The function that is responsible for deleting data"""
        cur = self.databse.cursor()
        date = int(date.toString('dd'))

        # Удаление данных из таблицы standart_outgo
        if self.table_name == 'standart':
            is_into = cur.execute(f"""SELECT * FROM standart_outgo
                                  WHERE dayid = {date}""")
            if is_into.fetchone() == None:
                self.label.setText('На данный день нет данных')
            else:
                cur.execute(f"""DELETE FROM standart_outgo 
                            WHERE dayid = {date}""")
                self.databse.commit()
                self.label.setText('Удаление прошло успешно')

        # Удаление данных из таблицы plan_outgo
        elif self.table_name == 'plan':
            is_into = cur.execute(f"""SELECT * FROM plan_outgo
                                  WHERE dayid = {date}""")
            if is_into.fetchone() == None:
                self.label.setText('На данный день нет данных')
            else:
                cur.execute(f"""DELETE FROM plan_outgo
                            WHERE dayid = {date}""")
                self.databse.commit()
                self.label.setText('Удаление прошло успешно')


# Класс отвечающий за окно информации о программе
class InfoWindow(QWidget):
    """The class responsible for the program information window"""

    def __init__(self):
        """initializer function"""
        super(InfoWindow, self).__init__()
        uic.loadUi('info.ui', self)
        self.setWindowTitle('О программе')
        self.info.setReadOnly(True)
        file = open('info.txt', mode='rt', encoding='utf-8')
        text = file.readlines()
        self.info.setPlainText(''.join(text))
        file.close()


# Класс отвечающий за окно вывода данных
class Output_Window(QWidget):
    """The class responsible for the data output window"""

    def __init__(self, name, data):
        """initializer function. Accepts file name and spending data"""
        super(Output_Window, self).__init__()
        uic.loadUi('output_window.ui', self)
        self.setWindowTitle('Вывод')
        im = QPixmap(name)
        self.lbl.setPixmap(im)
        self.lbl.resize(im.width(), im.height())
        self.info.setReadOnly(True)
        text = []
        text.append(f'Итого: {sum([date[1] for date in data])}')
        for date in data:
            if date[1] != 0:
                text.append(f'{date[0]}.'
                            f'{datetime.datetime.now().strftime("%m")}: '
                            f'{date[1]}')
        self.info.setPlainText('\n'.join(text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.exit(app.exec())
    sys.exit(app.exec())