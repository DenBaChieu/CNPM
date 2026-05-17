from datetime import datetime
from ParkingSlot import ParkingSlot
from Vehicle import Vehicle
import sqlite3
import secrets

def SetupParkingSessionDB():
    conn = sqlite3.connect("../Database/ParkingSession.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parkingSessions (
        sessionId TEXT PRIMARY KEY,
        entryTime TEXT NOT NULL,
        exitTime TEXT,
        sessionStatus TEXT NOT NULL,
        parkingSlotId TEXT NOT NULL,
        userId TEXT NOT NULL,
        licensePlate TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

class ParkingSession:
    sessionId: str
    entryTime: datetime
    exitTime: datetime
    sessionStatus: str # Active, Completed
    parkingSlot: ParkingSlot
    userId: str
    vehicle: Vehicle

    def __init__(self, parkingSlot: ParkingSlot, userId: str, vehicle: Vehicle):
        self.sessionId = secrets.token_hex(16) 
        self.entryTime = datetime.datetime.now()
        self.sessionStatus = "Active"
        self.parkingSlot = parkingSlot
        self.userId = userId
        self.vehicle = vehicle
        conn = sqlite3.connect("../Database/ParkingSession.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO parkingSessions (sessionId, entryTime, sessionStatus, parkingSlotId, userId, licensePlate) VALUES (?, ?, ?, ?, ?, ?)", 
                       (self.sessionId, self.entryTime.isoformat(), self.sessionStatus, parkingSlot.slotId, userId, vehicle.licensePlate))
        conn.commit()
        conn.close()

    def GetTotalTime(self):
        if self.sessionStatus == "Active":
            return (datetime.now() - self.entryTime).total_seconds() / 3600
        else:
            return (self.exitTime - self.entryTime).total_seconds() / 3600

    def CloseSession(self):
        self.exitTime = datetime.datetime.now()
        self.sessionStatus = "Completed"
        conn = sqlite3.connect("../Database/ParkingSession.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE parkingSessions SET exitTime = ?, sessionStatus = ? WHERE sessionId = ?", 
                       (self.exitTime.isoformat(), self.sessionStatus, self.sessionId))
        conn.commit()
        conn.close()

    def GenerateRecord(self):
        return {
            "sessionId": self.sessionId,
            "entryTime": self.entryTime.isoformat(),
            "exitTime": self.exitTime.isoformat() if self.exitTime else None,
            "totalTimeHours": self.GetTotalTime(),
            "sessionStatus": self.sessionStatus
        }