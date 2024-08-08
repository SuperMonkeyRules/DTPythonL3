import sys
import hashlib
import json

from PyQt6 import uic
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QTableView, QTableWidgetItem, QTableWidget, \
    QAbstractItemView

activeTeacher = None


def hashText(text):
    hashObject = hashlib.sha256()
    hashObject.update(text.encode())
    return hashObject.hexdigest()


def setActiveTeacher(teacher):
    global activeTeacher
    activeTeacher = teacher


def getActiveTeacher():
    return activeTeacher


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/mainPanel.ui', self)
        self.ui.activeTeachLABEL.setText(f'Teacher: {getActiveTeacher()}')

        self.ui.viewPaperBTN.clicked.connect(lambda: self.viewPapers())
        self.ui.createStudentBTN.clicked.connect(lambda: self.viewPapers())
        self.ui.createPaperBTN.clicked.connect(lambda: self.viewPapers())

        with open('data/paperInfo.json', 'r') as paperJSON:
            data = dict(json.load(paperJSON))

        for paper in data['papers']:
            self.ui.paperCOMBO.addItem(paper['name'])

    def viewPapers(self):
        selectedPaper = self.ui.paperCOMBO.currentText()
        paperPanel = PaperWindow(self, selectedPaper)
        paperPanel.show()


class PaperWindow(QMainWindow):
    def __init__(self, parent, chosenPaper):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/paperPanel.ui', self)
        self.chosenPaper = chosenPaper
        self.ui.gradeTABLE.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.populateTable()
        self.ui.refreshBTN.clicked.connect(lambda: self.populateTable())

    def populateTable(self):
        self.ui.gradeTABLE.clear()
        self.ui.gradeTABLE.setHorizontalHeaderLabels(['name', 'grade'])

        with open('data/gradesInfo.json', 'r') as gradesJSON:
            gradesData = dict(json.load(gradesJSON))

        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        with open('data/studentInfo.json', 'r') as studentJSON:
            studentData = dict(json.load(studentJSON))

        gradeData = []
        for grade in gradesData['grades']:
            for paper in paperData['papers']:
                if paper['name'] == self.chosenPaper:
                    selID = paper['id']
                break
            if grade['paper_id'] == selID:
                for student in studentData['students']:
                    if student['id'] == grade['student_id']:
                        studentName = student['name']
                        try:
                            gradeData.append([studentName, grade['grade']])
                        except UnboundLocalError:
                            pass
                        break

        self.ui.gradeTABLE.setRowCount(len(gradeData))
        row = 0
        for studentGrade in gradeData:
            col = 0
            for info in studentGrade:
                newItem = QTableWidgetItem(info)
                newItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.gradeTABLE.setItem(row, col, newItem)
                col += 1
            row += 1

        self.ui.gradeTABLE.setColumnWidth(0, int(self.ui.gradeTABLE.width() / 2))
        self.ui.gradeTABLE.resizeColumnToContents(1)
        self.ui.gradeTABLE.resizeRowsToContents()


class LoginWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/loginPanel.ui', self)
        self.ui.submitBTN.clicked.connect(lambda: self.login())

    def login(self):
        with open('data/loginInfo.json', 'r') as loginJSON:
            data = dict(json.load(loginJSON))

        loginTeach = self.ui.teacherCodeINPUT.text()
        loginPass = self.ui.passwordINPUT.text()
        hashedPass = hashText(loginPass)
        try:
            if data[loginTeach] == hashedPass:
                print('Correct password')
                setActiveTeacher(loginTeach)
                mainPanel = MainWindow()
                mainPanel.show()
                self.close()
            else:
                print('Incorrect password')
        except KeyError:
            print('User does not exist')


def main():
    app = QApplication(sys.argv)
    loginPanel = LoginWindow()
    loginPanel.show()
    sys.exit(app.exec())


main()
