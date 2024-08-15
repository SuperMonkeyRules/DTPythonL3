import sys
import hashlib
import json

from PyQt6 import uic
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QTableView, QTableWidgetItem, QTableWidget, \
    QAbstractItemView, QDialog, QDialogButtonBox, QLineEdit

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

        def createNew(creationType: str):
            creationType = creationWindow(creationType)
            creationType.show()

        def viewAllStudents():
            studentViewWindow = StudentWindow()
            studentViewWindow.show()
            print('Showing students')

        self.ui.viewPaperBTN.clicked.connect(lambda: self.viewPapers())
        self.ui.createStudentBTN.clicked.connect(lambda: createNew('student'))
        self.ui.createPaperBTN.clicked.connect(lambda: createNew('paper'))
        self.ui.viewStudentsBTN.clicked.connect(lambda: viewAllStudents())

        with open('data/paperInfo.json', 'r') as paperJSON:
            data = dict(json.load(paperJSON))

        for paper in data['papers']:
            self.ui.paperCOMBO.addItem(paper['name'])

    def viewPapers(self):
        selectedPaper = self.ui.paperCOMBO.currentText()
        paperPanel = PaperWindow(self, selectedPaper)
        paperPanel.show()


class StudentWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/studentPanel.ui', self)
        self.ui.studentTABLE.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.populateTable()
        self.ui.refreshBTN.clicked.connect(lambda: self.populateTable())

    def populateTable(self):
        self.ui.studentTABLE.clear()

        with open('data/gradesInfo.json', 'r') as gradesJSON:
            gradesData = dict(json.load(gradesJSON))

        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        with open('data/studentInfo.json', 'r') as studentJSON:
            studentData = dict(json.load(studentJSON))

        studentDataList = []
        for student in studentData['students']:
            currentStudent = [student['name']]
            currentPapers = []
            for entry in gradesData['grades']:
                if entry['student_id'] == student['id']:
                    for paper in paperData['papers']:
                        if entry['paper_id'] == paper['id']:
                            currentPapers.append(paper['name'])
            currentStudent.append(currentPapers)
            studentDataList.append(currentStudent)
        print(studentDataList)

        self.ui.studentTABLE.setRowCount(len(studentDataList))
        row = 0
        for studentGrade in studentDataList:
            col = 0
            for info in studentGrade:
                try:
                    newItem = QTableWidgetItem(info)
                except TypeError:
                    newItem = QTableWidgetItem(', '.join(info).upper())
                newItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.studentTABLE.setItem(row, col, newItem)
                col += 1
            row += 1

        self.ui.studentTABLE.setColumnWidth(0, int(self.ui.studentTABLE.width() / 2))
        self.ui.studentTABLE.resizeColumnToContents(1)
        self.ui.studentTABLE.resizeRowsToContents()


class PaperWindow(QMainWindow):
    def __init__(self, parent, chosenPaper):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/paperPanel.ui', self)
        self.ui.gradeTABLE.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.chosenPaper = chosenPaper
        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        for paper in paperData['papers']:
            if paper['name'] == self.chosenPaper:
                self.ui.paperLABEL.setText(f'{paper["name"]} - {paper["title"]}')

        self.populateTable()
        self.ui.refreshBTN.clicked.connect(lambda: self.populateTable())

    def populateTable(self):
        self.ui.gradeTABLE.clear()

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


class creationWindow(QDialog):
    def __init__(self, target: str, parent=None):
        QDialog.__init__(self, parent)
        self.ui = uic.loadUi('ui/creationPopup.ui', self)
        self.target = target
        if self.target == 'student':
            self.ui.descBOX.deleteLater()

        self.ui.creationLABEL.setText(f'Create {self.target.capitalize()}')
        self.ui.buttonBox.accepted.connect(lambda: self.acceptedCreation())

    def acceptedCreation(self):
        if self.target == 'paper':
            with open('data/paperInfo.json', 'r') as readPaper:
                data = dict(json.load(readPaper))
            paperID = len(data['papers'])
            paperName = self.ui.nameBOX.text()
            paperDesc = self.ui.descBOX.text()
            newPaper = {
                "id": paperID,
                "name": paperName,
                "title": paperDesc
            }
            data['papers'].append(newPaper)

            with open('data/paperInfo.json', 'w') as writePaper:
                json.dump(data, writePaper, indent=2)

            print('Created new paper')
        elif self.target == 'student':
            with open('data/studentInfo.json', 'r') as readStudent:
                data = dict(json.load(readStudent))

            print(data)
            studentID = len(data['students'])
            studentName = self.ui.nameBOX.text()
            newStudent = {
                "id": studentID,
                "name": studentName,
            }
            data['students'].append(newStudent)

            with open('data/studentInfo.json', 'w') as writeStudent:
                json.dump(data, writeStudent, indent=2)

            print('Created new student')
        else:
            raise 'somethings very wrong'
        pass


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
            for teacher in data['teachers']:
                if teacher['name'] == loginTeach:  # NAMES ARE TREATED AS UNIQUE
                    if teacher['password'] == hashedPass:
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
