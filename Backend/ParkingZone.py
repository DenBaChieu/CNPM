from User import *
from Vehicle import *

class ParkingZone:
    zoneId: str
    zoneName: str
    capacity: int
    status: str
    slots = []
    users: dict[User: Vehicle] = {}

    def __init__(self, zoneId: str, zoneName: str, slots: list):
        self.zoneId = zoneId
        self.zoneName = zoneName
        self.capacity = len(slots)
        self.status = "Open"
        self.slots = slots
        self.users = {}

    def UserEntered(self, user: User, vehicle: Vehicle):
        self.users[user] = vehicle

    def VehicleLeft(self, licensePlate: str):
        for key, value in self.users.items():
            if value.licensePlate == licensePlate:
                del self.users[key]
                return True
        return False

    def GetUserAndVehicleInZone(self, licensePlate: str) -> tuple[User, Vehicle]:
        for key, value in self.users.items():
            if value.licensePlate == licensePlate:
                return key, value
        return None, None

    def GetAvailableSlots(self):
        return [slot for slot in self.slots if slot.slotStatus == "Vacant"]
    
    def UpdateStatus(self, newStatus: str):
        self.status = newStatus

    def GetStatus(self):
        return self.status