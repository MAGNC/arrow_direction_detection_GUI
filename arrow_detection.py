# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'try0.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import cv2 as cv
import sys
import numpy as np
import tqdm
import time

class Handle:

    def __init__(self):
        self.thresh = 0.4
        self.template_left = self.get_outline('template_left.png')
        self.template_right = self.get_outline('template_right.png')
        self.template_up = self.get_outline('template_up.png')
        self.template_down = self.get_outline('template_down.png')
        self.target = self.get_outline(str(ui.openfile_name))
        self.target_origin = cv.imread(str(ui.openfile_name), cv.IMREAD_COLOR)#目的照片的三原色版
        # 拿到了模板和要匹配的图片

        self.template = [self.template_left, self.template_right, self.template_up, self.template_down]
        self.template_width = self.get_width_high(self.template)[0]
        self.template_high = self.get_width_high(self.template)[1]
        #分别获得了模板的长宽高

    def get_outline(self, location_of_picture):
        img = cv.imread(location_of_picture, cv.IMREAD_GRAYSCALE)
        after_canny = cv.Canny(img, 100, 200)
        # cv.imshow('{}after_canny'.format(location_of_picture), after_canny)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
        return after_canny


    def template_matching(self, template, target, matching_method):
        res = cv.matchTemplate(template, target, matching_method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        return min_loc, res


    def display_matching(self, template_res, threshold, target, width, high):  # 此函数画出匹配的部分
        loc = np.where(template_res >= threshold)  # 返回矩阵中大于阈值的位置
        for pt in zip(*loc[::-1]):  # zip(*loc)将loc的值转化为列表，然后再转化为元组，也就是所有的匹配结果的位置
            target = cv.rectangle(target, pt, (pt[0] + width, pt[1] + high), (0, 0, 255), 2)
        target = cv.cvtColor(target, cv.COLOR_BGR2RGB)
        self.plot(target)


    def get_width_high(self, template_set):
        template_width = [0, 0, 0, 0]
        template_high = [0, 0, 0, 0]
        for i in range(len(self.template)):
            template_width[i], template_high[i] = self.template[i].shape[::-1]
        print(template_width, template_high)
        return template_width, template_high


    def plot(self, converted_picture):
        cv.imshow("picture", converted_picture)
        cv.waitKey(0)
        cv.destroyAllWindows()


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class Ui_MainWindow(object):

    def __init__(self):
        self.openfile_name = None
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)

        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 261, 231))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(290, 180, 500, 300))
        self.textBrowser.setObjectName("textBrowser")

        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menumain = QtWidgets.QMenu(self.menubar)
        self.menumain.setObjectName("menumain")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.pushButton_3 = QtWidgets.QAction(MainWindow)
        self.pushButton_3.setObjectName("pushButton_3")
        self.menubar.addAction(self.menumain.menuAction())

        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(self.openfile)
        self.pushButton_2.clicked.connect(self.match)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)  # 即接收是从MainWindow来接收的

    def openfile(self):
        self.openfile_name, _ = QFileDialog.getOpenFileName(None, '选择文件', '', '*.png;;*.jpg')
        self.openfile_name = self.openfile_name.split('/')[-1]
        if not self.openfile_name:
            return
        print(self.openfile_name)
        #return self.openfile_name

    def match(self):
        print("开始匹配")
        a = Handle()
        start = time.time()

        # 拿到模板的宽和高

        all_match_matrix = []  # 拿到目标对于每个模板的匹配矩阵
        for single in a.template:
            b = np.asarray(a.template_matching(single, a.target, cv.TM_CCOEFF_NORMED)[1])
            all_match_matrix.append(b)

        count = [0, 0, 0, 0]
        print("开始寻找最佳匹配")
        for every_matrix, index, i in tqdm.tqdm(
                zip(all_match_matrix, [0, 1, 2, 3], [1, 2, 3, 4])):  # 对每个矩阵中的每一个相似值都和阈值相比较，超过就记1，看哪个超过阈值最多，哪个就最匹配
            every_matrix = every_matrix.reshape(every_matrix.size, 1)
            print("正在看第{}个模板".format(i))
            for x in tqdm.tqdm(np.nditer(every_matrix)):
                # 阵变成一行的矩阵，便于用nditor方法
                # print(x)
                if abs(x) > a.thresh:
                    count[index] += x

        # 找到最大相似度的模板
        # print(count)
        max_value = max(count)
        max_index = count.index(max_value)  # 找到最大值对应的被匹配的模板
        max_similar_template = a.template[max_index]
        # print(all_match_matrix[max_index])#打印每个像素的相似值矩阵
        end = time.time()
        print('Running time: %s Seconds' % (end - start))

        min_loc = a.template_matching(max_similar_template, a.target, cv.TM_CCOEFF_NORMED)[0]
        res = a.template_matching(max_similar_template, a.target, cv.TM_CCOEFF_NORMED)[1]
        a.display_matching(res, a.thresh, a.target_origin, a.template_width[max_index], a.template_high[max_index])

        # 转换RGB，输出对应模板
        converted_ = cv.cvtColor(a.template[max_index], cv.COLOR_BGR2RGB)
        a.plot(converted_)
        big = {}
        big[a.template[0]] = "left"
        big[a.template[1]] = "right"
        big[a.template[2]] = "up"
        big[a.template[3]] = "down"
        #call(['python', 'arrow_detection.py', '{}'.format(self.openfile_name)])
        print("箭头方向为{}".format(big[max_similar_template]))
        print("匹配结束")


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "select"))
        self.pushButton_2.setText(_translate("MainWindow", "match"))

        self.menumain.setTitle(_translate("MainWindow", "main"))
        self.pushButton_3.setText(_translate("MainWindow", "openfile"))
        self.pushButton_3.setToolTip(_translate("MainWindow", "打开文件"))

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # app.setWindowIcon(QIcon('images/horse.jpg'))

    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())
