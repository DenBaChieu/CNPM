from Vehicle import Vehicle
from ParkingSession import ParkingSession
from ParkingZone import ParkingZone
from ParkingSlot import ParkingSlot
from Sensor import *
from LogManager import LogManager

class ParkingManager:
    activeSessions: list[ParkingSession] = []
    managedZones: list[ParkingZone] = []
    parkingPolicy = None
    monitoring = False

    def __init__(self):
        self.activeSessions = []
        self.managedZones = []
        self.vehicles = []

    def GetZone(self, zoneId: str):
        for zone in self.managedZones:
            if zone.zoneId == zoneId:
                return zone
        return None

    def StartMonitor(self):
        self.monitoring = True
        LogManager.LogEvent("Parking monitoring started")

    def StopMonitor(self):
        self.monitoring = False
        LogManager.LogEvent("Parking monitoring stopped")

    def GetZoneFromSlot(self, slot: ParkingSlot) -> ParkingZone:
        for zone in self.managedZones:
            for s in zone.slots:
                if s.slotId == slot.slotId:
                    return zone
        return None

    def GetZoneFromSensor(self, sensor: Sensor) -> ParkingZone:
        for zone in self.managedZones:
            for s in zone.slots:
                if s.sensor.sensorId == sensor.sensorId:
                    return zone
        return None

    def StartParkingSession(self, licensePlate: str, slot: ParkingSlot):
        existing = next(
            (
                s for s in self.activeSessions
                if s.licensePlate == licensePlate
                and s.parkingSlotId == slot.slotId
                and s.sessionStatus == "Active"
            ),
            None
        )
        if existing:
            return existing

        session = ParkingSession(
            parkingSlotId=slot.slotId,
            zone=self.GetZoneFromSlot(slot),
            licensePlate=licensePlate
        )
        self.activeSessions.append(session)

        LogManager.LogEvent(
            f"Vehicle {licensePlate} parked in slot {slot.slotId}; session {session.sessionId} started"
        )
        return session

    def StopParkingSession(self, licensePlate: str, slot: ParkingSlot):
        session = next(
            (
                s for s in self.activeSessions
                if s.licensePlate == licensePlate
                and s.parkingSlotId == slot.slotId
                and s.sessionStatus == "Active"
            ),
            None
        )

        if not session:
            LogManager.LogEvent(
                f"No active session found for vehicle {licensePlate} at slot {slot.slotId}"
            )
            return None

        session.CloseSession()
        self.activeSessions.remove(session)

        LogManager.LogEvent(
            f"Vehicle {licensePlate} left slot {slot.slotId}; session {session.sessionId} completed"
        )
        return session.GenerateRecord()