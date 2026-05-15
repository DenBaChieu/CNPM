from datetime import datetime
from ParkingSlot import ParkingSlot
from Vehicle import Vehicle

class ParkingSession:
    sessionId: str
    entryTime: datetime
    exitTime: datetime
    sessionStatus: str # Active, Completed
    parkingSlot: ParkingSlot
    userId: str
    vehicle: Vehicle

    def __init__(self, sessionId: str, parkingSlot: ParkingSlot, userId: str, vehicle: Vehicle):
        self.sessionId = sessionId 
        self.entryTime = datetime.datetime.now()
        self.sessionStatus = "Active"
        self.parkingSlot = parkingSlot
        self.userId = userId
        self.vehicle = vehicle

    def GetTotalTime(self):
        if self.sessionStatus == "Active":
            return (datetime.now() - self.entryTime).total_seconds() / 3600
        else:
            return (self.exitTime - self.entryTime).total_seconds() / 3600

    def CloseSession(self):
        self.exitTime = datetime.datetime.now()
        self.sessionStatus = "Completed"

    def GenerateRecord(self):
        return {
            "sessionId": self.sessionId,
            "entryTime": self.entryTime.isoformat(),
            "exitTime": self.exitTime.isoformat() if self.exitTime else None,
            "totalTimeHours": self.GetTotalTime(),
            "sessionStatus": self.sessionStatus
        }