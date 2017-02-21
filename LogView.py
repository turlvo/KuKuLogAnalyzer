#-*- coding: utf-8 -*-

import pyqtgraph as pg
from DateAxis import DateAxis
from TableModel import TableModel
from PyQt4.QtGui import *
from PyQt4 import uic

class LogView(QTableView):
    def __init__(self, graphicLayout, layoutRow = 0, layoutCol = 0):
        super().__init__()
        self.view = graphicLayout.addPlot(axisItems={'bottom': DateAxis(orientation='bottom')}, row = layoutRow, col = layoutCol, rowspan = 1)
        self.view.setLimits(yMin = 0, yMax = 100)
        self.view.showGrid(x=True, y=False)

        self.viewLegend = self.view.addLegend()

    def show(self):
        self.view.show()
        self.viewLegend.show()

    def hide(self):
        self.view.hide()
        self.viewLegend.hide()

    def clear(self):
        self.view.clear()

    def autoRange(self):
        self.view.autoRange()

    def setLimits(self, **args):
        self.view.setLimits(**args)

    def showGrid(self, **args):
        self.view.showGrid(**args)

    def addLegend(self, **args):
        return self.view.addLegend(**args)

    def setXLink(self, target):
        self.view.setXLink(target.view)

    def getPlotView(self):
        return self.view

    # addPlot
    # Input :
    # - lineName : will be shown in graph for Legend
    # - x_values : values of X axis
    # - y_values : values of Y axis
    # - color : color of line. ex) 'r', 'g', 'b'
    # output : N/A
    def addPlot(self, lineName, x_values, y_values, color):
        fixedY_values = y_values

        if len(x_values) == len(y_values) == 0:
            return
        elif len(y_values) == 1:
            fixedY_values = [y_values[0] for _ in range(len(x_values))]

        self.view.plot(x=x_values, y=fixedY_values, name=lineName, pen=color, symbol='o')

    # addText
    # Input :
    # - x_values : values of X axis
    # - y_values : values of Y axis
    # - text_values : text values will be shown at graph
    # - color : color of Text. ex) 'red', 'green', 'blue'
    # output : N/A
    def addText(self, x_values, y_values, text_values, color):
        fixedY_values = y_values
        fixedTest_values = text_values

        if len(x_values) == len(y_values) == len(text_values) == 0:
            return

        if len(y_values) == 1:
            fixedY_values = [y_values[0] for _ in range(len(x_values))]

        if len(text_values) == 1:
            fixedTest_values = [text_values[0] for _ in range(len(x_values))]

        for x_value, y_value, text_value in zip(x_values, fixedY_values, fixedTest_values):
            text = pg.TextItem(
                    html='<div style="text-align: center"><span style="color:' + color
                         + '; font-size: 8pt;">' + text_value + '</span></div>', border='w')
            self.view.addItem(text)
            text.setPos(x_value, y_value)

    # addSpot
    # Input :
    # - x_values : values of X axis
    # - y_values : values of Y axis
    # - color : color of Spot. ex) 'r', 'g', 'b'
    # output : N/A
    def addSpot(self, x_values, y_values, color):
        fixedY_values = y_values

        if len(x_values) == len(y_values) == 0:
            return
        elif len(y_values) == 1:
            fixedY_values = [y_values[0] for _ in range(len(x_values))]

        spot = []
        for x_value, y_value in zip(x_values, fixedY_values):
            spot.append({'pos': (x_value, y_value), 'pen': {'color': color, 'width': 2}})

        point = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        point.addPoints(spot)
        self.view.addItem(point)



