import sqlite3
from pydantic import BaseModel
from LogManager import *

class CreateVehicleData(BaseModel):
    licensePlate: str
    vehicleType: str
    ownerId: int

class Vehicle:
    licensePlate: str
    vehicleType: str
    ownerId: int

    def __init__(self, licensePlate: str, vehicleType: str, ownerId: int):
        self.licensePlate = licensePlate
        self.vehicleType = vehicleType
        self.ownerId = ownerId

    def UpdateVehicleInfo(self, licensePlate: str, vehicleType: str):
        self.licensePlate = licensePlate
        self.vehicleType = vehicleType

def SetupVehicleDB():
    conn = sqlite3.connect("../Database/Vehicle.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle (
        licensePlate TEXT PRIMARY KEY,
        vehicleType TEXT,
        ownerId INTEGER
    )
    """)
    conn.commit()
    conn.close()

def RegisterVehicle(licensePlate: str, vehicleType: str, ownerId: int):
    conn = sqlite3.connect("../Database/Vehicle.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM vehicle WHERE licensePlate = ?",
        (licensePlate,)
    )

    existing = cursor.fetchone()

    if existing:
        print(f"Vehicle with license plate {licensePlate} already exists.")
        conn.close()
        return Vehicle(
            licensePlate=existing[0],
            vehicleType=existing[1],
            ownerId=existing[2],
        )

    cursor.execute("""
        INSERT INTO vehicle (
            licensePlate,
            vehicleType,
            ownerId
        )
        VALUES (?, ?, ?)
    """, (
        licensePlate,
        vehicleType,
        ownerId
    ))

    conn.commit()
    conn.close()

    newVehicle = Vehicle(
        licensePlate=licensePlate,
        vehicleType=vehicleType,
        ownerId=ownerId,
    )

    LogManager.LogEvent(f"Registered new vehicle with license plate {licensePlate}")

    return newVehicle

def GetVehicle(licensePlate: str):
    conn = sqlite3.connect("../Database/Vehicle.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM vehicle WHERE licensePlate = ?",
        (licensePlate,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return Vehicle(
            licensePlate=row[0],
            vehicleType=row[1],
            ownerId=row[2],
        )

    v = Vehicle(
        licensePlate=licensePlate,
        vehicleType=None,
        ownerId=None,
    )

    return v