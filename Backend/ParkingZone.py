class ParkingZone:
    zoneId: str
    zoneName: str
    capacity: int
    status: str
    slots = []

    def __init__(self, zoneId: str, zoneName: str, slots: list):
        self.zoneId = zoneId
        self.zoneName = zoneName
        self.capacity = len(slots)
        self.status = "Open"
        self.slots = slots

    def GetAvailableSlots(self):
        return [slot for slot in self.slots if slot.slotStatus == "Vacant"]
    
    def UpdateStatus(self, newStatus: str):
        self.status = newStatus

    def GetStatus(self):
        return self.status