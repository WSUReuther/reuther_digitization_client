# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projects.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Projects(object):
    def setupUi(self, Projects):
        Projects.setObjectName("Projects")
        Projects.resize(1277, 862)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Projects.sizePolicy().hasHeightForWidth())
        Projects.setSizePolicy(sizePolicy)
        Projects.setMinimumSize(QtCore.QSize(0, 0))
        self.gridLayout = QtWidgets.QGridLayout(Projects)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.projectsTable = QtWidgets.QTableWidget(Projects)
        self.projectsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.projectsTable.setColumnCount(8)
        self.projectsTable.setObjectName("projectsTable")
        self.projectsTable.setRowCount(0)
        self.verticalLayout_2.addWidget(self.projectsTable)
        self.addProjectBtn = QtWidgets.QPushButton(Projects)
        self.addProjectBtn.setObjectName("addProjectBtn")
        self.verticalLayout_2.addWidget(self.addProjectBtn)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Projects)
        QtCore.QMetaObject.connectSlotsByName(Projects)

    def retranslateUi(self, Projects):
        _translate = QtCore.QCoreApplication.translate
        Projects.setWindowTitle(_translate("Projects", "Projects"))
        self.addProjectBtn.setText(_translate("Projects", "Add Project"))
