#-*- coding: utf-8 -*-
import os
import shutil
import re
import datetime
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from WiFiEvent import WiFiEvent


class LogMergerThread(QThread):
    def __init__(self, folder, type):
        #super(LogMergerThread, self).__init__(folder)
        super(LogMergerThread, self).__init__()
        self.folder = folder
        self.type = type
        self.stopThread = False


    def run(self):
        self.bondLogFiles(self.folder, self.type)

    def bondLogFiles(self, dir, type):
        fullFileNameList = []
        outputFileName = os.path.join(dir, type + '.merged')

        fileList = glob.glob(dir+'\\' + type+'.log*')
        if len(fileList) == 0:
            self.emit(SIGNAL('MERGE_PERCENT'), 25)
            return

        mergefile = glob.glob(outputFileName)
        if len(mergefile) == 1:
            print(type, ' file is skipped')
            self.emit(SIGNAL('MERGE_LABEL'), type + ' file skipped')
            self.emit(SIGNAL('MERGE_PERCENT'), 25)
            return

        fullFileNameList = sorted(fileList, reverse=True)

        with open(outputFileName, 'wb') as outfile:
            for filename in fullFileNameList:
                if filename == outputFileName:
                    # don't want to copy the output into the output
                    continue
                with open(filename, 'rb') as readfile:
                    shutil.copyfileobj(readfile, outfile)
        print(type + ' merge is done')
        self.emit(SIGNAL('MERGE_LABEL'), type + ' file merged')
        self.emit(SIGNAL('MERGE_PERCENT'), 25)


class LogMerger(QDialog):
    def __init__(self, folder):
        super().__init__()
        self.ui = uic.loadUi("WaitDlg.ui")
        self.label = self.ui.progressLabel
        self.progressbar = self.ui.progressBar
        self.progressbarValue = 0

        self.logMainThread = LogMergerThread(folder, 'main')
        self.logMainThread.start()
        self.logSystemThread = LogMergerThread(folder, 'system')
        self.logSystemThread.start()
        self.logRadioThread = LogMergerThread(folder, 'radio')
        self.logRadioThread.start()
        self.logEventsThread = LogMergerThread(folder, 'events')
        self.logEventsThread.start()
        self.connect(self.logMainThread, SIGNAL('MERGE_PERCENT'), self.updateProgressBarPercent)
        self.connect(self.logMainThread, SIGNAL('MERGE_LABEL'), self.updateProgressBarLabel)
        self.connect(self.logSystemThread, SIGNAL('MERGE_PERCENT'), self.updateProgressBarPercent)
        self.connect(self.logSystemThread, SIGNAL('MERGE_LABEL'), self.updateProgressBarLabel)
        self.connect(self.logRadioThread, SIGNAL('MERGE_PERCENT'), self.updateProgressBarPercent)
        self.connect(self.logRadioThread, SIGNAL('MERGE_LABEL'), self.updateProgressBarLabel)
        self.connect(self.logEventsThread, SIGNAL('MERGE_PERCENT'), self.updateProgressBarPercent)
        self.connect(self.logEventsThread, SIGNAL('MERGE_LABEL'), self.updateProgressBarLabel)

        # self.logMainThread.join()
        # self.logSystemThread.join()
        # self.logRadioThread.join()
        # self.logEventsThread.join()
        self.ui.exec()  # modal

    def closeDlg(self):
        self.ui.close()

    def updateProgressBarLabel(self, msg):
        self.label.setText(msg)

    def updateProgressBarPercent(self, value):
        self.progressbarValue += value
        self.progressbar.setValue(self.progressbarValue)
        if self.progressbarValue == 100:
            self.closeDlg()


############################# Main ######################################
if __name__ == '__main__':
    bondLogFiles("D:\\Python\\KuKuLogAnalyzer\\temp", 'main')
    #mergeLogFilesByTime('.\\temp\\a\\main.log', '.\\temp\\a\\system.log')



def mergeLogFilesByTime(file1, file2):
    merged = []
    with open(file1, encoding='UTF8') as ifp1:
        for file1Line in ifp1:
            lineSplited1 = re.split('\s+', file1Line)
            print('file1', lineSplited1)
            if len(lineSplited1) < 6:
                continue
            with open(file2, encoding='UTF8') as ifp2:
                for file2Line in ifp2:
                    lineSplited2 = re.split('\s+', file2Line)
                    print('file2', lineSplited2)

                    if len(lineSplited2) < 6:
                        continue

                    t1 = datetime.datetime.strptime(lineSplited1[0] + ' ' + lineSplited1[1], "%m-%d %H:%M:%S.%f")
                    t2 = datetime.datetime.strptime(lineSplited2[0] + ' ' + lineSplited2[1], "%m-%d %H:%M:%S.%f")

                    if t1 < t2 :
                        merged.append(file1Line)
                        merged.append(file2Line)
                    else :
                        merged.append(file2Line)
                        merged.append(file1Line)

                    # date = datetime.datetime.strptime('2016-' + log[0] + ' ' + log[1][:-4], "%Y-%m-%d %H:%M:%S:%f")
                    # numDate = time.mktime(date.timetuple())
            # #print(lineSplited)
            # if len(lineSplited) > 5:
            #     date = lineSplited[0]
            #     time = lineSplited[1]
            #     pid = lineSplited[2]
            #     tid = lineSplited[3]
            #     level = lineSplited[4]
            #     tag = lineSplited[5][:-1]
            #     message = " ".join(lineSplited[6:])
# class LogMerger(QMainWindow):
#     def __init__(self, folder):
#         self.logmergeThread = LogMergerThread(folder)
#         self.logmergeThread.start()
#         self.waitUI = WaitUI()
#         self.connect(self.logmergeThread, SIGNAL('MERGE_PERCENT'), self.updateProgressBar)
#
#     def updateProgressBar(self, val):
#         self.waitUI.updateValue(val)

