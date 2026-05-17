from Sensor import *
from Vehicle import *

class ParkingSlot:
    slotId: str
    slotStatus: str # Occupied, Vacant
    slotType: str # Motorcycle, Car
    status: str # Available, Unavailable
    currentVehicleLicense: str
    sensor: Sensor
    StopParkingSession = None
    StartParkingSession = None

    def __init__(self, slotId: str, slotType: str, sensor: Sensor, StartParkingSession, StopParkingSession):
        self.slotId = slotId
        self.slotType = slotType
        self.sensor = sensor
        self.slotStatus = "Vacant"
        self.currentVehicleLicense = None
        self.sensor.AssignVehicle = self.AssignVehicle
        self.sensor.ReleaseSlot = self.ReleaseSlot
        self.StartParkingSession = StartParkingSession
        self.StopParkingSession = StopParkingSession

    def ReleaseSlot(self):
        if self.currentVehicleLicense:
            self.StopParkingSession(self.currentVehicleLicense, self)
        self.currentVehicleLicense = None
        self.slotStatus = "Vacant"

    def AssignVehicle(self, licensePlate: str):
        self.currentVehicleLicense = licensePlate
        self.slotStatus = "Occupied"
        self.StartParkingSession(licensePlate, self)

    def UpdateStatus(self, nextStatus: str):
        self.status = nextStatus

    def GetStatus(self):
        return self.status