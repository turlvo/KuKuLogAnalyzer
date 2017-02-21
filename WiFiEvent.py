
class WiFiEvent:
    def __init__(self, name, symbol, valuesNames):
        self.name = name
        self.symbol = symbol
        self.valuesNames = valuesNames
        self.values = []
        self.logs = []
        self.show = 0

    def getEventShow(self):
        return self.show

    def setEventShow(self, value):
        self.show = value

    def getEventName(self):
        return self.name

    def getEventSymbol(self):
        return self.symbol

    def getEventValuesName(self):
        return self.valuesNames

    def getEventValues(self):
        return self.values

    def setEventValues(self, value):
        self.values.append(value)

    def setEventLogs(self, log):
        self.logs.append(log)

    def getEventLogs(self):
        return self.logs

    def setEventToBeShown(self, value):
        self.show = value

    def getEventToBeShown(self):
        return self.show