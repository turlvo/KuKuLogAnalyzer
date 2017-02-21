#-*- coding: utf-8 -*-


import sys
import datetime
import time

from PyQt4.QtGui import *
from PyQt4 import uic

import pyqtgraph as pg

from DateAxis import DateAxis
from TableModel import TableModel
from LogMerger import LogMerger
from LogParser import LogParser
from LogView import LogView
from WiFiEvent import WiFiEvent

import ctypes
import os
import sys

if getattr(sys, 'frozen', False):
    # Override dll search path.
    ctypes.windll.kernel32.SetDllDirectoryW('C:/Users/ngj/AppData/Local/Continuum/Anaconda3/Library/bin/')
    # Init code to load external dll
    ctypes.CDLL('mkl_avx2.dll')
    ctypes.CDLL('mkl_def.dll')
    ctypes.CDLL('mkl_vml_avx2.dll')
    ctypes.CDLL('mkl_vml_def.dll')

    # Restore dll search path.
    ctypes.windll.kernel32.SetDllDirectoryW(sys._MEIPASS)

#################################### UI ######################################
class MainUI(QTableView):
    def __init__(self):
        super().__init__()

        self.column = ['Date', 'Time', 'PID', 'TID', 'Level', 'Tag', 'Message']
        self.logs = []
        self.events = []
        self.cbDict = {}
        self.vboxLayout = QVBoxLayout()

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # Load UI layout
        self.ui = uic.loadUi("MainUI.ui")

        # Log table init
        self.logTableInit()

        # Log GraphicView init
        self.logGraphicViewInit()

        # Menu init
        self.ui.actionRegister.triggered.connect(self.openDirectory)

        # LogTable Hide checkbox init
        self.ui.hideCheckbox.stateChanged.connect(self.changedTableHideCheckbox)

        self.ui.show()


    def openDirectory(self):

        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", "./"))

        if not folder:
            return
        logmerger = LogMerger(folder)
        logparser = LogParser(folder)
        self.events = logparser.getEvents()
        self.logs = logparser.getLogs()

        # for event in self.events:
        #     print(event.getEventName())
        #     print(event.getEventSymbol())
        #     print(event.getEventLogs())

        # Event Checkbox init
        self.eventCheckboxInit()

        # device MAC Label init
        self.ui.deviceMACLabel.setText(logparser.getDeviceMAC())

    def changedTableHideCheckbox(self, state):
        if state:
            self.ui.logTable.hide()
        else:
            self.ui.logTable.show()


    # logGraphicViewInit()
    # Input : None
    # Output : None
    # Note : Initialize GraphicViewWidget for log event graph
    def logGraphicViewInit(self):
        self.plotGraphList = []

        axis = DateAxis(orientation='bottom')
        #vb = CustomViewBox()

        # OnOff LogGrpahicView
        #self.FirstGraphView = self.ui.logGraphicView.addPlot(axisItems={'bottom': DateAxis(orientation='bottom')}, row = 0, col = 0, rowspan = 1)
        self.FirstGraphView = LogView(self.ui.logGraphicView, 0, 0)
        self.FirstGraphView.setLimits(yMin = 0, yMax = 100)
        self.FirstGraphView.showGrid(x=True, y=False)

        self.FirstGraphViewLegend = self.FirstGraphView.addLegend()

        # Value LogGrpahicView
        #self.SecondGraphView = self.ui.logGraphicView.addPlot(axisItems={'bottom': DateAxis(orientation='bottom')}, row = 1, col = 0, rowspan = 1)
        self.SecondGraphView = LogView(self.ui.logGraphicView, 1, 0)
        self.SecondGraphView.setLimits(yMin = 0, yMax = 100)
        self.SecondGraphView.showGrid(x=True, y=False)
        self.SecondGraphView.hide()

        self.SecondGraphViewLegend = self.SecondGraphView.addLegend()
        self.SecondGraphViewLegend.hide()

        # Link with ValueLogGraphicView and StateLogGraphicView
        #self.FirstGraphView.getPlotView().setXLink(self.SecondGraphView.getPlotView())
        self.FirstGraphView.setXLink(self.SecondGraphView)
        #self.OnOffLogGraphicView.setYLink(self.ValueLogGraphicView)


        # Test
        #self.ThirdGraphView = LogView(self.ui.logGraphicView,2, 0)
        #self.ThirdGraphView.addPlot('test', [1,2,3,4], [1,2,3,4], 'r')
        #self.ThirdGraphView.addText([1,2,3,4], [1,2,3,4], ['a', 'b', 'c', 'd'], 'red')
        #self.ThirdGraphView.addSpot([1, 2, 3, 4], [4, 3, 2, 1], 'b')



    # RemoveAllLogGraphicView()
    # Input : None
    # Output : None
    # Note : Remove all plot graph in logGraphicView
    def RemoveAllLogGraphicView(self):
        for plot in self.plotGraphList:
            self.FirstGraphViewLegend.removeItem(plot)
            self.SecondGraphViewLegend.removeItem(plot)
        #self.logGraphicLegend.legend = None
        # self.logGraphicView.removeItem(self.logGraphicViewLegend)
        self.FirstGraphView.clear()
        self.SecondGraphView.clear()

        self.SecondGraphView.hide()
        self.SecondGraphViewLegend.hide()

    # updateGraphicView()
    # Input : None
    # Output : None
    # Note : Draw plot graph using WiFi event
    def updateGraphicView(self):
        #ColList = 'mcrgbk'
        ColList = 'bgrmky'
        ColListName = ['blue', 'green', 'red', 'magenta', 'black', 'yellow']

        isFirst = True
        firstGraphView = self.FirstGraphView
        secondGraphView = self.SecondGraphView
        targetView = firstGraphView
        #ThirdGraphView = self.ThirdGraphView

        for event in self.events:
            if event.getEventToBeShown() == True:
                eventName = event.getEventName()
                targetView = self.FirstGraphView

                if eventName == "WiFi_ONOFF":
                    if isFirst == True:
                        isFirst = False
                    self.updateOnOffGraphic(firstGraphView, event, ('b', 'blue'))
                elif eventName == "HOTSPOT":
                    if isFirst == True:
                        isFirst = False
                    self.updateOnOffGraphic(firstGraphView, event, ('g', 'green'))
                elif eventName == "AIRPLANE":
                    if isFirst == True:
                        isFirst = False
                    self.updateOnOffGraphic(firstGraphView, event, ('m', 'magenta'))
                elif eventName == "LCD_ONOFF":
                    if isFirst == True:
                        isFirst = False
                    self.updateOnOffGraphic(firstGraphView, event, ('k', 'black'))
                elif eventName == "RSSI":
                    if isFirst == True:
                        isFirst = False
                    self.updateValueGraphic(firstGraphView, event, ('r', 'red'))
                elif eventName == "WiFi_STATE":
                    if isFirst == True:
                        targetView = firstGraphView
                    else:
                        targetView = secondGraphView
                    self.updateStateGraphic(targetView, event, ('b', 'blue'))
                elif eventName == "WiFi_STATE*WiFi_CONNECTED" or eventName == "WiFi_STATE*WiFi_DISCONNECTED":
                    if isFirst == True:
                        targetView = firstGraphView
                    else:
                        targetView = secondGraphView
                    self.updateConnectGraphic(targetView, event, ('r', 'red'))
                elif eventName == "WiFi_STATE*SCAN":
                    if isFirst == True:
                        targetView = firstGraphView
                    else:
                        targetView = secondGraphView
                    self.updateScanGraphic(targetView, event, ('m', 'magenta'))
                elif eventName == "HOTSPOT_STATE":
                    if isFirst == True:
                        targetView = firstGraphView
                    else:
                        targetView = secondGraphView
                    self.updateStateGraphic(targetView, event, ('r', 'red'))
                elif eventName == "HOTSPOT_STATE*CLIENT_CONNECTED" or eventName == "HOTSPOT_STATE*CLIENT_DISCONNECTED":
                    if isFirst == True:
                        targetView = firstGraphView
                    else:
                        targetView = secondGraphView
                    self.updateConnectGraphic(targetView, event, ('r', 'red'))

        firstGraphView.autoRange()
        secondGraphView.autoRange()

    def updateScanGraphic(self, view, event, color):
        view.show()

        x_values = []
        y_values = [0.7]
        text_values = ['Scan']

        for log in event.getEventLogs():
            # X value
            date = datetime.datetime.strptime('2016-' + log[1] + ' ' + log[2][:-4], "%Y-%m-%d %H:%M:%S")
            numDate = time.mktime(date.timetuple())
            x_values.append(numDate)

        view.setLimits(yMin=0, yMax=1.2, minYRange=1.2)

        # Show Text 'Scan'
        view.addText(x_values, y_values, text_values, color[1])

        # Show Spot
        view.addSpot(x_values, y_values, color[0])


    def updateValueGraphic(self, view, event, color):
        view.show()
        self.SecondGraphViewLegend.show()

        x_values = []
        y_values = []
        text_values = []

        for value, log in zip(event.getEventValues(), event.getEventLogs()):
            # Y value
            absY = abs(int(value['rssi']))
            y_values.append(absY)

            # X value
            date = datetime.datetime.strptime('2016-' + log[1] + ' ' + log[2][:-4], "%Y-%m-%d %H:%M:%S")
            numDate = time.mktime(date.timetuple())
            x_values.append(numDate)

            # Show more information at graph
            text_values.append('-' + str(absY))

        view.addText(x_values, y_values, text_values, color[1])

        # Draw line
        x_values, y_values = self.adjRSSI(x_values, y_values)
        view.setLimits(yMin=0, yMax=max(y_values) + 10, minYRange=max(y_values) + 10)
        view.addPlot(event.getEventName(), x_values, y_values, color[0])

        self.plotGraphList.append(event.getEventName())

    def updateOnOffGraphic(self, view, event, color):
        view.show()
        self.FirstGraphViewLegend.show()

        x_values = []
        y_values = []
        text_values = []
        text_y_values = []

        for value, log in zip(event.getEventValues(), event.getEventLogs()):
            # Y value
            if value['enabled'] == 'True' or value['enabled'] == 'true':
                y_values.append(30)
            elif value['enabled'] == 'False' or value['enabled'] == 'false':
                y_values.append(0)
            elif value['enabled'] == 'ACTION_SCREEN_ON':
                y_values.append(20)
            elif value['enabled'] == 'ACTION_SCREEN_OFF':
                y_values.append(0)

            # X value
            date = datetime.datetime.strptime('2016-' + log[1] + ' ' + log[2][:-4], "%Y-%m-%d %H:%M:%S")
            numDate = time.mktime(date.timetuple())
            x_values.append(numDate)

            adjY = 33
            # Show more information at graph
            eventName = event.getEventName()
            willBeShownData = ""
            if eventName == "WiFi_ONOFF":
                willBeShownData = str(value['AppLable'])
            elif eventName == "AIRPLANE":
                willBeShownData = "Airplane: " + value['enabled']
            elif eventName == "LCD_ONOFF" and value['enabled'] == "ACTION_SCREEN_ON":
                willBeShownData = "LCD: On"
                adjY = 22
            elif eventName == "LCD_ONOFF" and value['enabled'] == "ACTION_SCREEN_OFF":
                willBeShownData = "LCD: Off"
                adjY = 22
            text_values.append(willBeShownData)
            text_y_values.append(adjY)

        view.addText(x_values, text_y_values, text_values, color[1])

        # To change analog signal to digital signal
        (x_values, y_values) = self.changeFromAnalogToDigital(x_values, y_values)

        # Draw line
        view.setLimits(yMin=0, yMax=100, minYRange=100)
        view.addPlot(event.getEventName(), x_values, y_values, color[0])

        self.plotGraphList.append(event.getEventName())

    def updateStateGraphic(self, view, event, color):
        targetView = view
        targetView.show()
        self.SecondGraphViewLegend.show()

        x_values = []
        y_values = []
        text_values = []
        text_y_values = []

        for value, log in zip(event.getEventValues(), event.getEventLogs()):
            # Y value
            state = value['state']
            adjY = 0
            if state == '[DISCONNECTED]' or state == 'WIFI_AP_STATE_DISABLED':
                adjY = 0
            elif state == '[CONNECTED]' or state == 'WIFI_AP_STATE_ENABLED':
                adjY = 1
            elif state == '[CONNECTING]':
                adjY = 0.25
            elif state == '[AUTHENTICATING]' or state == 'WIFI_AP_STATE_ENABLING' or state == 'WIFI_AP_STATE_DISABLING':
                adjY = 0.5
            elif state == '[OBTAINING_IPADDR]':
                adjY = 0.75
            elif state == '[SCANNING]':
                continue
            y_values.append(adjY)

            # X value
            date = datetime.datetime.strptime('2016-' + log[1] + ' ' + log[2][:-4], "%Y-%m-%d %H:%M:%S")
            numDate = time.mktime(date.timetuple())
#            temp.append(date)
            x_values.append(numDate)

            # Show more information at graph
            if value['state'] == '[DISCONNECTED]' or value['state'] == 'WIFI_AP_STATE_DISABLED':
                adjY = 0.1
            text_values.append(value['state'])
            text_y_values.append(adjY)

        view.addText(x_values, text_y_values, text_values, color[0])

        # To change analog signal to digital signal
        (x_values, y_values) = self.changeFromAnalogToDigital(x_values, y_values)

        # Draw line
        targetView.setLimits(yMin=0, yMax=max(y_values) + 0.2, minYRange=max(y_values) + 0.2)
        view.addPlot(event.getEventName(), x_values, y_values, color[0])

        self.plotGraphList.append(event.getEventName())

    def updateConnectGraphic(self, view, event, color):
        targetView = view
        targetView.show()
        self.SecondGraphViewLegend.show()

        x_values = []
        y_values = []
        text_values = []
        text_y_values = []

        if len(event.getEventLogs()) > 0:
            for value, log in zip(event.getEventValues(), event.getEventLogs()):
                eventName = event.getEventName()
                # Y value
                adjY = 0
                if eventName == 'WiFi_STATE*WiFi_CONNECTED' or eventName == 'HOTSPOT_STATE*CLIENT_CONNECTED':
                    adjY = 1
                else:
                    adjY = 0
                y_values.append(adjY)

                # X value
                date = datetime.datetime.strptime('2016-' + log[1] + ' ' + log[2][:-4], "%Y-%m-%d %H:%M:%S")
                numDate = time.mktime(date.timetuple())
                x_values.append(numDate)

                # Show more information at graph
                willBeShownData = value['mac']
                if eventName.find("WiFi_DISCONNECTED") > 0:
                    willBeShownData = value['mac'] + ' Reason: ' + value['reason']
                    adjY = 0.15
                elif eventName.find("WiFi_CONNECTED") > 0:
                    willBeShownData = value['mac']
                    adjY = 1.1
                elif eventName.find("CLIENT_CONNECTED") > 0:
                    willBeShownData = 'connected: <br>' + value['mac']
                    adjY = 1.1
                elif eventName.find("CLIENT_DISCONNECTED") > 0:
                    willBeShownData = 'disconnected: <br>' + value['mac']
                    adjY = 0.15
                text_y_values.append(adjY)
                text_values.append(willBeShownData)

            view.addText(x_values, text_y_values, text_values, color[0])

            # Draw line
            #targetView.setLimits(yMin=0, yMax=max(y_value) + 0.2, minYRange=max(y_value) + 0.2)

            view.addSpot(x_values, y_values, color[0])



    # changeFromAnalogToDigital()
    # Input : List, List
    # Output : List, List
    # Note : change line data from analog to digital
    def changeFromAnalogToDigital(self, x_values, y_values):
        # To change analog signal to digital signal
        x_value_changed = []
        y_value_changed = []
        if y_values[0] == 30:
            x_value_changed.append(x_values[0])
            y_value_changed.append(0)
        # elif y_values[0] == 0:
        #     x_value_changed.append(x_values[0] - 3)
        #     y_value_changed.append(1)
        #     x_value_changed.append(x_values[0])
        #     y_value_changed.append(1)

        x_value_changed.append(x_values[0])
        y_value_changed.append(y_values[0])
        for index in range(1, len(y_values)):
            # # stop by wrong reverse date
            # if x_values[index - 1] > x_values[index]:
            #     x_value_changed.append(x_values[index-1])
            #     y_value_changed.append(0)

            if y_values[index - 1] != y_values[index]:
                y_value_changed.append(y_values[index - 1])
                x_value_changed.append(x_values[index])
            x_value_changed.append(x_values[index])
            y_value_changed.append(y_values[index])



        if y_values[len(y_values)-1] == 1:
            y_value_changed.append(1)
            x_value_changed.append(x_values[len(x_values)-1]+3)



        return (x_value_changed, y_value_changed)

    # logTableInit()
    # Input : None
    # Output : None
    # Note : Initialize 'TableModel' tableWidget for logs
    def logTableInit(self):

        self._tm = TableModel(self, [], self.column)
        self.ui.logTable.setModel(self._tm)

        self.ui.logTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.logTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.logTable.setSelectionMode(QAbstractItemView.SingleSelection);
        self.ui.logTable.resizeColumnsToContents()

    # updateLogToTable()
    # Input : Logs will be shown at Table
    # Output : None
    # Note : Insert each logs to tableWidget
    def updateLogToTable(self, logs):
        self._tm = TableModel(self, logs, self.column)
        self.ui.logTable.setModel(self._tm)
        self.ui.logTable.resizeColumnsToContents()


    # removeAllLog()
    # Input : None
    # Output : None
    # Note : Erase all data in tableWidget
    def removeAllLog(self):
        # remove all row data
        self.ui.logTable.setModel(None)

    # eventCheckboxInit()
    # Input : None
    # Output : None
    # Note : Initialize WiFi event checkbox
    def eventCheckboxInit(self):
        self.eventCheckboxDeinit(self.vboxLayout)
        self.cb_All = QCheckBox('All')
        self.cb_All.stateChanged.connect(self.changedEventCheckbox)
        self.cbDict['All'] = self.cb_All
        self.vboxLayout.addWidget(self.cb_All)

        for event in self.events:
            eventName = event.getEventName()
            if eventName.find('*') > 0:
                continue
            if len(event.getEventLogs()) > 0:
                cb_Temp = ('cb_' + event.getEventName())
                self.cb_Temp = QCheckBox(event.getEventName())
                self.cb_Temp.stateChanged.connect(self.changedEventCheckbox)
                self.cbDict[event.getEventName()] = self.cb_Temp
                self.vboxLayout.addWidget(self.cb_Temp)
        self.ui.eventListGroupbox.setLayout(self.vboxLayout)

    def eventCheckboxDeinit(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    # changedEventCheckbox()
    # Input : checked state
    # Output : None
    # Note : Add or remove log at tableWidget by checking checkbox
    def changedEventCheckbox(self, state):
        cb = self.sender()
        shownLogsList = []

        if cb.text() == 'All':
            if state != 0:
                for otherCb in self.cbDict.values():
                    if otherCb != cb:
                        otherCb.setChecked (False)
                cb.setChecked(True)
        else:
            if self.cbDict['All'].isChecked() == True:
                self.cbDict['All'].setChecked(False)
                return

        if self.cbDict['All'].isChecked() == True:
            #self.removeAllLog()
            for event in self.events:
                if len(event.getEventLogs()) > 0:
                    event.setEventToBeShown(True)
                    shownLogsList += event.getEventLogs()
            #self.updateLogToTable(self.logs)
            shownLogsList = sorted(shownLogsList, key=lambda element: (element[0]))
            shownLogsList = [x[1:] for x in shownLogsList]
            self.updateLogToTable(shownLogsList)
            self.updateGraphicView()
        else:
            for event in self.events:
                eventName = event.getEventName()
                if eventName.find('*') > 0:
                    continue
                if len(event.getEventLogs()) > 0 and self.cbDict[eventName].isChecked() == True:
                    event.setEventToBeShown(True)
                    shownLogsList += event.getEventLogs()

                    # Link between 'WiFi_STATE' and 'WiFi_CONNECTED' & 'WiFi_DISCONNECTED'
                    if eventName == 'WiFi_STATE' or eventName == 'HOTSPOT_STATE':
                        for e in self.events:
                            ename = e.getEventName()
                            if ename.startswith(eventName + '*'):
                                e.setEventToBeShown(True)
                                shownLogsList += e.getEventLogs()
                else:
                    event.setEventToBeShown(False)

                    # Link between 'WiFi_STATE' and 'WiFi_CONNECTED' & 'WiFi_DISCONNECTED'
                    if event.getEventName() == 'WiFi_STATE' or eventName == 'HOTSPOT_STATE':
                        for e in self.events:
                            ename = e.getEventName()
                            if ename.startswith(eventName + '*'):
                                e.setEventToBeShown(False)


            self.removeAllLog()
            self.RemoveAllLogGraphicView()
            if len(shownLogsList) > 0:
                shownLogsList = sorted(shownLogsList, key=lambda element: (element[0]))
                shownLogsList = [x[1:] for x in shownLogsList]

                self.updateLogToTable(shownLogsList)
                self.updateGraphicView()

    def adjRSSI(self, x_values, y_values):
        x_modified = []
        y_modified = []

        for loop in range(len(x_values)):
            if (loop+1) < len(x_values) and x_values[loop+1] - x_values[loop] > 4:
                x_modified.append(x_values[loop])
                y_modified.append(y_values[loop])
                x_modified.append(x_values[loop])
                y_modified.append(0)
                x_modified.append(x_values[loop+1])
                y_modified.append(0)

            else:
                x_modified.append(x_values[loop])
                y_modified.append(y_values[loop])

        return (x_modified, y_modified)



############################# Main ######################################
if __name__ == '__main__':

    # eventList = readEventFromFile('event')
    # logsDF = readLogsFromFile(eventList,'./temp/main.merged')
    #logsDF = readLogsFromFile(eventList, './temp/hotspot.log')
    #pyqtgraph.examples.run()

    app = QApplication(sys.argv)
    mainDlg = MainUI()


    app.exec()
    # DataFrame by 'Tag'
    #wifiOnOff = logsDF[(logsDF["Tag"]).find("wpa_supplicant")]
    #print(wifiOnOff)

    # for logRow in logsDF.iterrows():
    #     #print(logRow['Message'])
    #     #print('**** : ', type(logRow[1]['Message']), logRow[1]['Message'])
    #     if (logRow[1]['Message'].find("setWifiEnabled") > 0):
    #          print(logRow)


