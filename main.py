import sys
import hashlib
import json

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

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


class LoginWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('ui/loginPanel.ui', self)
        self.ui.submitBTN.clicked.connect(lambda: self.login())

    def login(self):
        with open('loginInfo.json', 'r') as loginJSON:
            data = dict(json.load(loginJSON))

        print(data)

        loginTeach = self.ui.teacherCodeINPUT.text()
        loginPass = self.ui.passwordINPUT.text()

        hashedPass = hashText(loginPass)

        print(loginTeach)
        print(loginPass)
        print(hashedPass)

        try:
            if data[loginTeach] == hashedPass:
                print('Correct password')
                setActiveTeacher(loginTeach)
            else:
                print('Incorrect password')
        except KeyError:
            print('User does not exist')


def main():
    setActiveTeacher('test')
    app = QApplication(sys.argv)
    loginPanel = LoginWindow()
    loginPanel.show()

    if getActiveTeacher() is not None:
        loginPanel.close()
        mainPanel = MainWindow()
        mainPanel.show()

    sys.exit(app.exec())


main()
