from datetime import datetime
from LogManager import *

class Sensor:
    sensorId: str
    occupancyStatus: str # Occupied, Vacant
    connectionStatus: str # Active, Inactive
    lastUpdatedTime: datetime
    ReleaseSlot = None
    AssignVehicle = None

    def __init__(self, sensorId: str):
        self.sensorId = sensorId
        self.occupancyStatus = "Vacant"
        self.connectionStatus = "Active"
        self.lastUpdatedTime = datetime.now()

    def DetectVehicle(self, licensePlate: str):
        if self.connectionStatus == "Inactive":
            print(f"Sensor {self.sensorId} is inactive. Cannot detect vehicle.")
            return

        if licensePlate:
            if self.occupancyStatus == "Vacant":
                self.AssignVehicle(licensePlate)
            self.occupancyStatus = "Occupied"
            self.lastUpdatedTime = datetime.now()
        else:
            if self.occupancyStatus == "Occupied":
                self.ReleaseSlot()
            self.occupancyStatus = "Vacant"
            self.lastUpdatedTime = datetime.now()

    def ReportFailure(self):
        LogManager.LogEvent(f"Sensor {self.sensorId} has a failure")
        self.connectionStatus = "Inactive"
        self.occupancyStatus = "Vacant"
        self.lastUpdatedTime = datetime.now()

    def Reconnect(self):
        LogManager.LogEvent(f"Sensor {self.sensorId} is back online")
        self.connectionStatus = "Active"
        self.occupancyStatus = "Vacant"
        self.lastUpdatedTime = datetime.now()