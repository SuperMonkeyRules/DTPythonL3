import hashlib
import json
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView, QDialog, QLineEdit, \
    QMessageBox, QComboBox

activeTeacher = None

def hashText(text: str):
    """
    Hashes the input text and returns a hexadecimal.

    :param text: The text to be hashed.
    :return: The hashed text as a hexadecimal string.
    """
    hashObject = hashlib.sha256()
    hashObject.update(text.encode())
    return hashObject.hexdigest()


def setActiveTeacher(teacher: str):
    """
    Sets the global variable activeTeacher to the specified teacher.

    :param teacher: The teacher to set as active.
    """
    global activeTeacher
    activeTeacher = teacher


def getActiveTeacher():
    """
    Retrieves the current value of the global variable activeTeacher.

    :return: The current active teacher.
    """
    return activeTeacher

class messageBox(QMessageBox):
    """
    An easily adjustable message box.

    :param title: Title of the message box
    :param text: Text of the message box
    """
    def __init__(self, title, text):
        QMessageBox.__init__(self)
        self.setStyleSheet("QLabel{min-width: 150px;}")
        self.setWindowTitle(title)
        self.setText(text)


class MainWindow(QMainWindow):
    """
    The main application window that manages the primary interface for
    viewing and creating students, papers, and managing grades.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/mainPanel.ui', self)
        self.ui.activeTeachLABEL.setText(f'Teacher: {getActiveTeacher()}')
        self.populatePapers()

        def createNew(creationType: str):
            """
            Creates the student/paper creation window.

            :param creationType:
            """
            creationType = creationWindow(creationType, self)
            creationType.show()

        def viewAllStudents():
            """
            Opens the student viewer.
            """
            studentViewWindow = StudentWindow()
            studentViewWindow.show()

        def openGradeManager():
            """
            Opens the grade manager.
            """
            gradeManagementWindow = gradeManager()
            gradeManagementWindow.show()


        self.ui.viewPaperBTN.clicked.connect(lambda: self.viewPapers())
        self.ui.createStudentBTN.clicked.connect(lambda: createNew('student'))
        self.ui.createPaperBTN.clicked.connect(lambda: createNew('paper'))
        self.ui.viewStudentsBTN.clicked.connect(lambda: viewAllStudents())
        self.ui.markStudentBTN.clicked.connect(lambda: openGradeManager())


    def populatePapers(self):
        """
        Populates the papers dropdown with papers from the stored JSON
        """
        # Clear all papers
        self.ui.paperCOMBO.clear()

        # Get all papers
        with open('data/paperInfo.json', 'r') as paperJSON:
            data = dict(json.load(paperJSON))

        # Populate dropdown with papers
        for paper in data['papers']:
            self.ui.paperCOMBO.addItem(paper['name'])

    def viewPapers(self):
        """
        Opens a new PaperWindow to display information about the selected paper.
        """
        selectedPaper = self.ui.paperCOMBO.currentText()
        paperPanel = PaperWindow(self, selectedPaper)
        paperPanel.show()


class gradeManager(QMainWindow):
    """
    Manages the grade management window,
    The grade management window contains multiple dropdowns for marking a student.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/gradePanel.ui', self)
        self.populateStudents()
        self.populatePapers()
        self.populateGrades()

        self.ui.gradeSUBMIT.accepted.connect(lambda: self.submitGrade())
        self.ui.gradeSUBMIT.rejected.connect(lambda: self.close())

    def submitGrade(self):
        """
        Grade submitter.
        Update or Add new grade.
        """
        success = False
        paperID = None
        studentID = None
        teacherID = None

        # Open all files
        with open('data/gradesInfo.json', 'r') as gradesJSON:
            gradesData = dict(json.load(gradesJSON))

        with open('data/loginInfo.json', 'r') as teacherJSON:
            teacherData = dict(json.load(teacherJSON))

        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        with open('data/studentInfo.json', 'r') as studentJSON:
            studentData = dict(json.load(studentJSON))

        newGrade = self.ui.gradeCB.currentText()

        # Convert all words to IDs
        for studentInfo in studentData['students']:
            if studentInfo['name'] == self.ui.studentCB.currentText():
                studentID = studentInfo['id']
                break

        for teacherInfo in teacherData['teachers']:
            if teacherInfo['name'] == getActiveTeacher():
                teacherID = teacherInfo['id']
                break

        for paperInfo in paperData['papers']:
            if paperInfo['name'] == self.ui.paperCB.currentText():
                paperID = paperInfo['id']
                break

        if None in [studentID, teacherID, paperID]:
            messageBox('Marking Status', "Couldn't find one of:\nStudent,\nTeacher,\nPaper").exec()
            return

        changeType = ''
        # Find the grade to be updated
        for gradeInfo in gradesData['grades']:
            if gradeInfo['paper_id'] == paperID and gradeInfo['student_id'] == studentID:
                gradeInfo['grade'] = newGrade
                gradeInfo['teacher_id'] = teacherID
                success = True
                changeType = 'Updated'
                break

        # If it wasn't updated add it
        if not success:
            gradeInfo = {'student_id': studentID,
                         'paper_id': paperID,
                         'grade': newGrade,
                         'teacher_id': teacherID}
            gradesData['grades'].append(gradeInfo)
            changeType = 'Added'

        with open('data/gradesInfo.json', 'w') as writeGrades:
            json.dump(gradesData, writeGrades, indent=2)

        messageBox('Marking Status', f'Successfully {changeType}').exec()


    def populateStudents(self):
        """
        Fill student dropdown
        """
        self.ui.studentCB.clear()

        with open('data/studentInfo.json', 'r') as studentJSON:
            studentData = dict(json.load(studentJSON))

        for student in studentData['students']:
            self.ui.studentCB.addItem(student['name'])

    def populatePapers(self):
        """
        Fill paper dropdown
        """
        self.ui.paperCB.clear()

        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        for paper in paperData['papers']:
            self.ui.paperCB.addItem(paper['name'])

    def populateGrades(self):
        """
        Fill grade dropdown
        """
        self.ui.gradeCB.clear()
        listOfGrades = ['A', 'B', 'C', 'D']

        for grade in listOfGrades:
            for i in range(0, 3):
                if i == 0:
                    self.ui.gradeCB.addItem(f'{grade}+')
                if i == 1:
                    self.ui.gradeCB.addItem(grade)
                if i == 2:
                    self.ui.gradeCB.addItem(f'{grade}-')


class StudentWindow(QMainWindow):
    """
    Manages the student view window, displaying students and their current papers.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/studentPanel.ui', self)
        self.ui.studentTABLE.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.populateTable()
        self.ui.refreshBTN.clicked.connect(lambda: self.populateTable())

    def populateTable(self):
        """
        Populates the table with student names, their current papers.
        """
        self.ui.studentTABLE.clear()
        self.ui.studentTABLE.setHorizontalHeaderLabels(['NAME', 'PAPERS'])

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

        self.ui.studentTABLE.setRowCount(len(studentDataList))
        row = 0
        for singleStudentData in studentDataList:
            col = 0
            for info in singleStudentData:
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
    """
    Manages the display of grades for a specific paper.
    """
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
        """
        Fill grades table
        """
        self.ui.gradeTABLE.clear()
        self.ui.gradeTABLE.setHorizontalHeaderLabels(['NAME', 'GRADE', 'MARKED BY'])

        with open('data/gradesInfo.json', 'r') as gradesJSON:
            gradesData = dict(json.load(gradesJSON))

        with open('data/paperInfo.json', 'r') as paperJSON:
            paperData = dict(json.load(paperJSON))

        with open('data/studentInfo.json', 'r') as studentJSON:
            studentData = dict(json.load(studentJSON))

        with open('data/loginInfo.json', 'r') as teacherJSON:
            teacherData = dict(json.load(teacherJSON))

        gradeData = []
        selID = None
        studentName = None
        teacherName = None
        for grade in gradesData['grades']:
            for paper in paperData['papers']:
                if paper['name'] == self.chosenPaper:
                    selID = paper['id']
                    break
            if grade['paper_id'] == selID:
                for student in studentData['students']:
                    if student['id'] == grade['student_id']:
                        studentName = student['name']
                for teacher in teacherData['teachers']:
                    if teacher['id'] == grade['teacher_id']:
                        teacherName = teacher['name']

                try:
                    gradeData.append([studentName, grade['grade'], teacherName])
                except UnboundLocalError:
                    pass

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

        self.ui.gradeTABLE.setColumnWidth(0, int(self.ui.gradeTABLE.width() / 3))
        self.ui.gradeTABLE.setColumnWidth(1, int(self.ui.gradeTABLE.width() / 3))
        self.ui.gradeTABLE.resizeColumnToContents(2)
        self.ui.gradeTABLE.resizeRowsToContents()


class creationWindow(QDialog):
    """
    Paper/Student creation window
    """
    def __init__(self, target: str, parent=None):
        QDialog.__init__(self, parent)
        self.ui = uic.loadUi('ui/creationPopup.ui', self)
        self.target = target
        if self.target == 'student':
            self.ui.descBOX.deleteLater()

        self.ui.creationLABEL.setText(f'Create {self.target.capitalize()}')
        self.ui.buttonBox.accepted.connect(lambda: self.acceptedCreation())

    def acceptedCreation(self):
        """
        Create new paper or student.
        Write out to persistent storage.
        """

        if not self.ui.nameBOX.text() or not self.ui.descBOX.text():
            messageBox('Creation Status', 'Failed to create entry').exec()
            return

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

            messageBox('Creation Status', f'Created new paper\n{paperName}').exec()
        elif self.target == 'student':
            with open('data/studentInfo.json', 'r') as readStudent:
                data = dict(json.load(readStudent))

            studentID = len(data['students'])
            studentName = self.ui.nameBOX.text()
            newStudent = {
                "id": studentID,
                "name": studentName,
            }
            data['students'].append(newStudent)

            with open('data/studentInfo.json', 'w') as writeStudent:
                json.dump(data, writeStudent, indent=2)

            messageBox('Creation Status', f'Created new student\n{studentName}').exec()
        else:
            raise 'somethings very wrong'


class LoginWindow(QMainWindow):
    """
    The login window,
    The login window shows immediately when the program is run
    and contains two text boxes and a button.
    Hashing is used for the passwords.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/loginPanel.ui', self)
        self.ui.submitBTN.clicked.connect(lambda: self.login())
        self.ui.passwordINPUT.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        with open('data/loginInfo.json', 'r') as loginJSON:
            data = dict(json.load(loginJSON))

        loginTeach = self.ui.teacherCodeINPUT.text()
        loginPass = self.ui.passwordINPUT.text()
        hashedPass = hashText(loginPass)
        for teacher in data['teachers']:
            if teacher['name'] == loginTeach:  # NAMES ARE TREATED AS UNIQUE
                if teacher['password'] == hashedPass:
                    setActiveTeacher(loginTeach)
                    mainPanel = MainWindow()
                    mainPanel.show()
                    self.close()
                    messageBox('Login Status', 'Successful').exec()
                else:
                    messageBox('Login Status', 'Failed').exec()
        if getActiveTeacher() is None:
            messageBox('Login Status', 'Failed').exec()


def main():
    app = QApplication(sys.argv)
    loginPanel = LoginWindow()
    loginPanel.show()
    sys.exit(app.exec())


main()
