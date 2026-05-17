from datetime import datetime
from ParkingSlot import ParkingSlot
from Vehicle import Vehicle
from ParkingZone import *
from User import *
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
        userId INT,
        zoneId TEXT NOT NULL,
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
    parkingSlotId: str
    userId: str
    zone: ParkingZone
    licensePlate: str

    def __init__(self, parkingSlotId: str, zone: ParkingZone, licensePlate: str):
        self.sessionId = secrets.token_hex(16)
        self.entryTime = datetime.now()
        self.sessionStatus = "Active"
        self.parkingSlotId = parkingSlotId
        self.zone = zone
        user, vehicle = zone.GetUserAndVehicleInZone(licensePlate)
        self.userId = user.userId
        self.licensePlate = licensePlate
        conn = sqlite3.connect("../Database/ParkingSession.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO parkingSessions (sessionId, entryTime, sessionStatus, parkingSlotId, userId, zoneId, licensePlate) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                        (self.sessionId, self.entryTime.isoformat(), self.sessionStatus, parkingSlotId, self.userId, zone.zoneId, licensePlate))
            conn.commit()
        finally:
            conn.close()

    def GetTotalTime(self):
        if self.sessionStatus == "Active":
            return (datetime.now() - self.entryTime).total_seconds() / 3600
        else:
            return (self.exitTime - self.entryTime).total_seconds() / 3600

    def CloseSession(self):
        self.exitTime = datetime.now()
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
    
def PrintAllSessions():
    conn = sqlite3.connect("../Database/ParkingSession.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parkingSessions")
    sessions = cursor.fetchall()

    conn.close()

    if not sessions:
        print("No parking sessions found.")
        return

    for session in sessions:
        print(f"""
                Session ID: {session[0]}
                Entry Time: {session[1]}
                Exit Time: {session[2]}
                Status: {session[3]}
                Parking Slot ID: {session[4]}
                User ID: {session[5]}
                License Plate: {session[6]}
                ----------------------------------------
            """)