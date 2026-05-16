from Vehicle import Vehicle
from ParkingSession import ParkingSession
from ParkingZone import ParkingZone
from ParkingSlot import ParkingSlot
from LogManager import LogManager


class ParkingManager:
    activeSessions: list[ParkingSession] = []
    managedZones: list[ParkingZone] = []
    parkingPolicy = None
    monitoring = False
    vehicles = []

    def __init__(self):
        self.activeSessions = []
        self.managedZones = []
        self.vehicles = []

    def StartMonitor(self):
        self.monitoring = True
        LogManager.LogEvent("Parking monitoring started")

    def StopMonitor(self):
        self.monitoring = False
        LogManager.LogEvent("Parking monitoring stopped")

    def GetVehicle(self, licensePlate: str):
        v = next((v for v in self.vehicles if v.licensePlate == licensePlate), None)
        if not v:
            v = Vehicle(
                vehicleId=f"V{len(self.vehicles)+1}",
                licensePlate=licensePlate,
                vehicleType="Unknown",
                ownerId="Unknown",
            )
            self.vehicles.append(v)
        return v

    def StartParkingSession(self, vehicle: Vehicle, slot: ParkingSlot):
        existing = next(
            (
                s for s in self.activeSessions
                if s.vehicle.licensePlate == vehicle.licensePlate
                and s.parkingSlot.slotId == slot.slotId
                and s.sessionStatus == "Active"
            ),
            None
        )
        if existing:
            return existing

        session = ParkingSession(
            sessionId=f"S{len(self.activeSessions)+1}",
            parkingSlot=slot,
            userId=vehicle.ownerId,
            vehicle=vehicle,
        )
        self.activeSessions.append(session)

        LogManager.LogEvent(
            f"Vehicle {vehicle.licensePlate} parked in slot {slot.slotId}; session {session.sessionId} started"
        )
        return session

    def StopParkingSession(self, vehicle: Vehicle, slot: ParkingSlot):
        session = next(
            (
                s for s in self.activeSessions
                if s.vehicle.licensePlate == vehicle.licensePlate
                and s.parkingSlot.slotId == slot.slotId
                and s.sessionStatus == "Active"
            ),
            None
        )

        if not session:
            LogManager.LogEvent(
                f"No active session found for vehicle {vehicle.licensePlate} at slot {slot.slotId}"
            )
            return None

        session.CloseSession()
        self.activeSessions.remove(session)

        LogManager.LogEvent(
            f"Vehicle {vehicle.licensePlate} left slot {slot.slotId}; session {session.sessionId} completed"
        )
        return session.GenerateRecord()

    def RegisterVehicle(self, vehicleId: str, licensePlate: str, vehicleType: str, ownerId: str):
        existing = next((v for v in self.vehicles if v.licensePlate == licensePlate), None)
        if existing:
            print(f"Vehicle with license plate {licensePlate} already exists.")
            return existing

        if not vehicleId:
            vehicleId = f"V{len(self.vehicles)+1}"

        newVehicle = Vehicle(
            vehicleId=vehicleId,
            licensePlate=licensePlate,
            vehicleType=vehicleType,
            ownerId=ownerId,
        )

        self.vehicles.append(newVehicle)
        LogManager.LogEvent(f"Registered new vehicle with license plate {licensePlate}")
        return newVehicle