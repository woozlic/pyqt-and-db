# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(246, 140)
        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 222, 116))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_info = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_info.setAlignment(QtCore.Qt.AlignCenter)
        self.label_info.setObjectName("label_info")
        self.verticalLayout.addWidget(self.label_info)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_username = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_username.setObjectName("label_username")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_username)
        self.edit_username = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.edit_username.setObjectName("edit_username")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edit_username)
        self.label_password = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_password.setObjectName("label_password")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_password)
        self.edit_password = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.edit_password.setObjectName("edit_password")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.edit_password)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_login = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.btn_login.setObjectName("btn_login")
        self.horizontalLayout_2.addWidget(self.btn_login)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Log in"))
        self.label_info.setText(_translate("Form", "Please, provide your credentials."))
        self.label_username.setText(_translate("Form", "Username"))
        self.label_password.setText(_translate("Form", "Password"))
        self.btn_login.setText(_translate("Form", "Login"))
