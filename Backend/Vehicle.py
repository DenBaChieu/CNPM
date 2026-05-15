class Vehicle:
    vehicleId: str
    licensePlate: str
    vehicleType: str
    ownerId: str

    def __init__(self, vehicleId: str, licensePlate: str, vehicleType: str, ownerId: str):
        self.vehicleId = vehicleId
        self.licensePlate = licensePlate
        self.vehicleType = vehicleType
        self.ownerId = ownerId

    def UpdateVehicleInfo(self, licensePlate: str, vehicleType: str):
        self.licensePlate = licensePlate
        self.vehicleType = vehicleType