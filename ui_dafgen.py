# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dafgen.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPlainTextEdit,
    QPushButton, QSizePolicy, QSlider, QWidget)

class Ui_DAFGen(object):
    def setupUi(self, DAFGen):
        if not DAFGen.objectName():
            DAFGen.setObjectName(u"DAFGen")
        DAFGen.resize(451, 95)
        DAFGen.setMinimumSize(QSize(451, 95))
        DAFGen.setMaximumSize(QSize(451, 95))
        font = QFont()
        font.setPointSize(11)
        DAFGen.setFont(font)
        self.delayLabel = QLabel(DAFGen)
        self.delayLabel.setObjectName(u"delayLabel")
        self.delayLabel.setGeometry(QRect(20, 10, 61, 21))
        self.delayLabel.setFont(font)
        self.actualDelayLabel = QLabel(DAFGen)
        self.actualDelayLabel.setObjectName(u"actualDelayLabel")
        self.actualDelayLabel.setGeometry(QRect(20, 50, 91, 31))
        self.actualDelayLabel.setFont(font)
        self.startButton = QPushButton(DAFGen)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setGeometry(QRect(200, 50, 71, 31))
        self.stopButton = QPushButton(DAFGen)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setGeometry(QRect(280, 50, 71, 31))
        self.quitButton = QPushButton(DAFGen)
        self.quitButton.setObjectName(u"quitButton")
        self.quitButton.setGeometry(QRect(360, 50, 71, 31))
        self.delaySlider = QSlider(DAFGen)
        self.delaySlider.setObjectName(u"delaySlider")
        self.delaySlider.setGeometry(QRect(120, 10, 241, 21))
        self.delaySlider.setMinimum(50)
        self.delaySlider.setMaximum(200)
        self.delaySlider.setOrientation(Qt.Horizontal)
        self.delayEdit = QPlainTextEdit(DAFGen)
        self.delayEdit.setObjectName(u"delayEdit")
        self.delayEdit.setGeometry(QRect(370, 10, 61, 31))
        self.delayEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.delayEdit.setReadOnly(True)
        self.actualDelayEdit = QPlainTextEdit(DAFGen)
        self.actualDelayEdit.setObjectName(u"actualDelayEdit")
        self.actualDelayEdit.setGeometry(QRect(120, 50, 61, 31))
        self.actualDelayEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.actualDelayEdit.setReadOnly(True)

        self.retranslateUi(DAFGen)

        QMetaObject.connectSlotsByName(DAFGen)
    # setupUi

    def retranslateUi(self, DAFGen):
        DAFGen.setWindowTitle(QCoreApplication.translate("DAFGen", u"DAF Gen", None))
        self.delayLabel.setText(QCoreApplication.translate("DAFGen", u"Delay", None))
        self.actualDelayLabel.setText(QCoreApplication.translate("DAFGen", u"Actual Delay", None))
        self.startButton.setText(QCoreApplication.translate("DAFGen", u"Start", None))
        self.stopButton.setText(QCoreApplication.translate("DAFGen", u"Stop", None))
        self.quitButton.setText(QCoreApplication.translate("DAFGen", u"Quit", None))
    # retranslateUi

