import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QLineEdit, QPushButton, QFileDialog, QMessageBox

__author__ = 'eoubrayrie'


lastDir = os.path.expandvars('$HOME')
# or, better, save & take it from config file:
# file_path =  os.path.join(QDir.home().absolutePath(), ".application_name")


class FileValidator(QValidator):
    def __init__(self, *args):
        super().__init__(*args)

    def validate(self, s, pos):
        if os.path.isfile(s):
            return QValidator.Acceptable, s, pos
        return QValidator.Intermediate, s, pos

    def fixup(self, s):
        pass


class Picker(QtWidgets.QWidget):  # TODO composition instead of inheritance

    def __init__(self, title, label='Select', exists=True, save=False, filters=None):
        super(Picker, self).__init__()
        self.save = save
        self.title = title
        self.filters = filters

        hbox = QtWidgets.QHBoxLayout()
        if exists:
            self.wtext = ValidatedLineEdit(FileValidator(), self)
        else:
            self.wtext = QLineEdit(self)
        self.wtext.setMinimumWidth(300)
        hbox.addWidget(self.wtext)
        # Expose some methods
        self.textChanged = self.wtext.textChanged
        self.hasAcceptableInput = self.wtext.hasAcceptableInput
        self.set_text = self.wtext.setText

        # self.icon = QtWidgets.QIcon.fromTheme("places/user-folders")
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)
        # self.icon.addPixmap(QPixmap(":/icons/folder_16x16.gif"), QtWidgets.QIcon.Normal, QtWidgets.QIcon.Off)
        self.wbtn = QPushButton(icon, label, self)

        self.wbtn.clicked.connect(self.pick)
        hbox.addWidget(self.wbtn)
        self.setLayout(hbox)

    @pyqtSlot()
    def pick(self):
        dlg = QFileDialog(self, self.title, lastDir, self.filters)
        if self.save:
            dlg.setDefaultSuffix(self._extension)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
        else:
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            dlg.setFileMode(QFileDialog.ExistingFile)
        if not dlg.exec():
            return

        self.wtext.setText(dlg.selectedFiles()[0])

    def get_text(self):
        return self.wtext.text()


class ValidatedLineEdit(QLineEdit):
    """ http://snorf.net/blog/2014/08/09/using-qvalidator-in-pyqt4-to-validate-user-input/ """

    def __init__(self, validator, *args):
        super().__init__(*args)

        self.setValidator(validator)
        self.textChanged.connect(self.check_state)
        self.textChanged.emit(self.text())  # check initial text

    @pyqtSlot()
    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)


class MinuteSecondEdit(ValidatedLineEdit):

    def __init__(self, *args):
        regexp = QtCore.QRegExp('^(([0-9]?[0-9]:?)?[0-5][0-9]:?)?[0-5][0-9]$')
        validator = QtGui.QRegExpValidator(regexp)
        super().__init__(validator, *args)

        self.setValidator(validator)
        self.textChanged.connect(self.check_state)
        self.textChanged.emit(self.text())  # check initial text

    def get_time(self):
        t = self.text()
        if len(t) > 2 and ':' not in t:
            t = t[:-2] + ':' + t[-2:]
        if len(t) > 5 and ':' not in t[:-5]:
            t = t[:-5] + ':' + t[-5:]
        return t

    def get_h_m_s(self):
        t = self.get_time()
        if len(t) < 8:
            t = '00:00:00'[:8 - len(t)] + t
        h = int(t[0:2])
        m = int(t[3:5])
        s = int(t[6:8])
        return h, m, s


class BiggerMessageBox(QMessageBox):

    # This is a much better way to extend __init__
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeGripEnabled(True)  # ... but still not resizable
        self.resize(self.sizeHint())

    def resizeEvent(self, event):
        result = super().resizeEvent(event)

        details_box = self.findChild(QtWidgets.QTextEdit)
        if details_box is not None:
            details_box.setFixedSize(details_box.sizeHint())  # not good
            details_box.setFixedSize(1000, 700)

        return result