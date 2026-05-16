import datetime


class TemporaryTicket:
    ticketId: str
    issueTime: datetime.datetime
    status: str  # ISSUED, CANCELLED
    licensePlate: str
    zoneId: str
    gateId: str

    def __init__(self, ticketId: str, licensePlate: str, zoneId: str, gateId: str):
        self.ticketId = ticketId
        self.issueTime = datetime.datetime.now()
        self.status = "ISSUED"
        self.licensePlate = licensePlate
        self.zoneId = zoneId
        self.gateId = gateId

    def CancelTicket(self):
        self.status = "CANCELLED"

    def GenerateRecord(self):
        return {
            "ticketId": self.ticketId,
            "licensePlate": self.licensePlate,
            "zoneId": self.zoneId,
            "gateId": self.gateId,
            "issueTime": self.issueTime.isoformat(),
            "status": self.status,
        }