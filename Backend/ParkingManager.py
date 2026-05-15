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
        #TODO

    def StopMonitor(self):
        self.monitoring = False
        LogManager.LogEvent("Parking monitoring stopped")
        #TODO

    def GetVehicle(self, licensePlate: str):
        v = next((v for v in self.vehicles if v.licensePlate == licensePlate), None)
        if not v:
            v = Vehicle(vehicleId=f"V{len(self.vehicles)+1}", licensePlate=licensePlate, vehicleType="Unknown", ownerId="Unknown")
        return v
    
    def StartParkingSession(self, vehicle: Vehicle, slot: ParkingSlot):
        LogManager.LogEvent(f"Vehicle {vehicle.licensePlate} parked in slot {slot.slotId}")
        #TODO
        #Create new parking session and add to activeSessions

    def StopParkingSession(self, vehicle: Vehicle, slot: ParkingSlot):
        LogManager.LogEvent(f"Vehicle {vehicle.licensePlate} left slot {slot.slotId}")
        #TODO
        #Find active session for this vehicle and slot, close it and remove from activeSessions

    def RegisterVehicle(self, vehicleId: str, licensePlate: str, vehicleType: str, ownerId: str):
        if self.GetVehicle(licensePlate):
            print(f"Vehicle with license plate {licensePlate} already exists.")
            return

        if not vehicleId:
            vehicleId = f"V{len(self.vehicles)+1}"

        newVehicle = Vehicle(vehicleId=vehicleId, licensePlate=licensePlate, vehicleType=vehicleType, ownerId=ownerId)
        self.vehicles.append(newVehicle)
        LogManager.LogEvent(f"Registered new vehicle with license plate {licensePlate}")