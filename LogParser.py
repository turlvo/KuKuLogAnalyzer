# -*- coding: utf-8 -*-
import os
import re
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from WiFiEvent import WiFiEvent

class LogParsingThread(QThread):
    def __init__(self, folder):
        super(LogParsingThread, self).__init__()
        self.folder = folder
        self.events = []
        self.logs = []
        self.deviceMAC = 'Device MAC <00:00:00:00:00:00>'
        self.stopThread = False

    def run(self):
        self.events = self.readEventFromFile('event')
        self.emit(SIGNAL('PARSE_LABEL'), 'events is parsed')

        self.logs = self.readLogsFromFile(self.events, self.folder)
        self.emit(SIGNAL('PARSE_LABEL'), 'The all log is parsed')

    def getEvents(self):
        return self.events

    def getLogs(self):
        return self.logs

    def getDeviceMAC(self):
        return self.deviceMAC

    # readLogsFromFile
    # Input : File name
    # Output : List [(date, time, pid, tid, level, tag, message)]
    #           List [update wifiEvent.eventValues]
    def readLogsFromFile(self, eventList, folder):
        logs_list = []
        column = ['Date', 'Time', 'PID', 'TID', 'Level', 'Tag', 'Message']

        toBeParsedFileList = []
        filesLength = 0
        fileIndex = 0
        cnt = 0

        self.emit(SIGNAL('PARSE_LABEL'), 'The log parsing will be started')
        for file in glob.glob(folder+"\\*.merged"):
            fullName = os.path.join(folder, file)
            toBeParsedFileList.append(fullName)
            filesLength += self.file_len(fullName)

        #print(toBeParsedFileList)
        if len(toBeParsedFileList) > 0:
            for filename in toBeParsedFileList:
                with open(filename, encoding="ISO-8859-1") as ifp:
                    for index, line in enumerate(ifp):
                        # Stop thread by user's cancel
                        if self.stopThread == True:
                            return
                        cnt = index
                        percent = ((fileIndex + cnt) / filesLength) * 100
                        self.emit(SIGNAL('PARSE_LABEL'), 'Parsing logs...<br>' + '(' + str(fileIndex+cnt) + ' / ' + str(filesLength) + ')')
                        self.emit(SIGNAL('PARSE_PERCENT'), percent)

                        lineSplited = re.split('\s+', line)
                        #print(lineSplited)
                        if len(lineSplited) > 5:
                            date = lineSplited[0]
                            time = lineSplited[1]
                            pid = lineSplited[2]
                            tid = lineSplited[3]
                            level = lineSplited[4]
                            tag = lineSplited[5][:-1]
                            message = " ".join(lineSplited[6:])

                            # Find device own MAC address and save
                            if message.startswith('MAC Addr from driver'):
                                split = re.split(r" |=|,|(?<![0-9])", message)
                                self.deviceMAC = 'Device MAC <' + split[6] + '>'

                            # print('log: %s, %s, %s, %s, %s, %s, %s' %(date, time, pid, tid, level, tag, message))
                            for event in eventList:
                                if message.startswith(event.getEventSymbol()):
                                    # T.T Because 'setWifiEnabled' is duplicated, add more if state
                                    if event.getEventSymbol() == "setWifiEnabled" and message.find("App Lable") == -1:
                                        continue

                                    messageSplited = re.split(r" |=|,|(?<![0-9])", message)

                                    if len(event.getEventValuesName()) > 0:
                                        maxValue = max(event.getEventValuesName().values())
                                        #print (messageSplited)
                                        if len(messageSplited) > int(maxValue):
                                            parsedValues = {}

                                            for k, v in event.getEventValuesName().items():
                                                parsedValues[k] = messageSplited[int(v)]
                                            event.setEventValues(parsedValues)

                                    event.setEventLogs((index, date, time, pid, tid, level, tag, message))
                                    # print((index, date, time, pid, tid, level, tag, message))

                            # log_series = Series([date, time, pid, tid, level, tag, message], column)
                            logs_list.append((date, time, pid, tid, level, tag, message))

                self.emit(SIGNAL('PARSE_LARBEL'), filename + ' is parsed')
                fileIndex += cnt
        else:
            self.emit(SIGNAL('PARSE_LARBEL'), 'NO LOGS')
        self.emit(SIGNAL('PARSE_DONE'))
        return logs_list

    # readEventFromFile
    # Input : File name
    # Output : List [ {'name': String, 'tag': String, 'values': List }, ...]
    def readEventFromFile(self, filename):

        eventList = []

        with open(filename) as ifp:
            for line in ifp:
                #splitEvent = line.split(',')
                splitEvent = re.split("\,+\s*", line)
                splitEvent[len(splitEvent) - 1] = splitEvent[len(splitEvent) - 1][:-1]

                name = splitEvent[0]
                symbol = splitEvent[1]

                valuesDict = {}
                if len(splitEvent) > 2:
                    values = splitEvent[2:]
                    for i in range(0, len(values), 2):
                        valuesDict[values[i]] = values[i + 1]

                event = WiFiEvent(name, symbol, valuesDict)
                eventList.append(event)

        return eventList

    def file_len(self, fname):
        length = 0
        with open(fname, encoding="ISO-8859-1") as f:
            for i, l in enumerate(f):
                length = i
        print(fname, length)
        return length


class LogParser(QDialog):
    def __init__(self, folder):
        super(LogParser, self).__init__()

        self.ui = uic.loadUi("WaitDlg.ui")
        self.ui.setWindowTitle('LogParser')
        self.label = self.ui.progressLabel
        self.progressbar = self.ui.progressBar
        self.progressbarValue = 0

        self.logParsingThread = LogParsingThread(folder)
        self.logParsingThread.start()
        self.connect(self.logParsingThread, SIGNAL('PARSE_PERCENT'), self.updateProgressBarPercent)
        self.connect(self.logParsingThread, SIGNAL('PARSE_LABEL'), self.updateProgressBarLabel)
        self.connect(self.logParsingThread, SIGNAL('PARSE_DONE'), self.closeDlg)
        self.connect(self, SIGNAL('triggered()'), self.closeEvent)
        self.ui.exec()  # modal

    def closeEvent(self, event):
        print("Closing")
        self.destory()

    def closeDlg(self):
        self.ui.close()

    def updateProgressBarLabel(self, msg):
        self.label.setText(msg)

    def updateProgressBarPercent(self, value):
        self.progressbar.setValue(value)

    def getEvents(self):
        return self.logParsingThread.getEvents()

    def getLogs(self):
        return self.logParsingThread.getEvents()

    def getDeviceMAC(self):
        return self.logParsingThread.getDeviceMAC()



############################# Main ######################################
if __name__ == '__main__':
    for f in glob.glob("*.merged"):
        print(f)
    # mergeLogFilesByTime('.\\temp\\a\\main.log', '.\\temp\\a\\system.log')

