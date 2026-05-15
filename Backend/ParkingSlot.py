from Sensor import *
from Vehicle import *

class ParkingSlot:
    slotId: str
    slotStatus: str # Occupied, Vacant
    slotType: str # Motorcycle, Car
    status: str # Available, Unavailable
    currentVehicle: Vehicle
    sensor: Sensor
    GetVehicle = None
    StopParkingSession = None
    StartParkingSession = None

    def __init__(self, slotId: str, slotType: str, sensor: Sensor, GetVehicle, StartParkingSession, StopParkingSession):
        self.slotId = slotId
        self.slotType = slotType
        self.sensor = sensor
        self.slotStatus = "Vacant"
        self.currentVehicle = None
        self.sensor.AssignVehicle = self.AssignVehicle
        self.sensor.ReleaseSlot = self.ReleaseSlot
        self.GetVehicle = GetVehicle
        self.StartParkingSession = StartParkingSession
        self.StopParkingSession = StopParkingSession

    def ReleaseSlot(self):
        if self.currentVehicle:
            self.StopParkingSession(self.currentVehicle, self)
        self.currentVehicle = None
        self.slotStatus = "Vacant"

    def AssignVehicle(self, licensePlate: str):
        vehicle = self.GetVehicle(licensePlate)
        self.currentVehicle = vehicle
        self.slotStatus = "Occupied"
        self.StartParkingSession(vehicle, self)

    def UpdateStatus(self, nextStatus: str):
        self.status = nextStatus

    def GetStatus(self):
        return self.status