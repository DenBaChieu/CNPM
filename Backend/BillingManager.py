import datetime

class BillingManager:
    def __init__(self):
        pass

class Ticket:
    ticketId: str
    amount: float
    issuedTime: datetime
    expirationTime: datetime
    status: str

    def CloseTicket(self):
        self.status = "Closed"

    def UpdateStatus(self, newStatus: str):
        self.status = newStatus

    def GetStatus(self):
        return self.status

class Payment:
    paymentId: str
    amount: float
    paymentDate: datetime
    status: str

    def __init__(self, paymentId: str, amount: float, paymentDate: datetime):
        self.paymentId = paymentId
        self.amount = amount
        self.paymentDate = datetime.datetime.now()
        self.status = "Pending"

    def CalculateTotal(self):
        pass

    def ProcessPayment(self):
        pass

    def GetPaymentURL(self):
        pass

    def GenerateReceipt(self):
        pass

    #When a vehicle exit, if it is temporary vehicle, we will generate a ticket
    def Exit(self):
        pass

    def UpdateStatus(self, newStatus: str):
        self.status = newStatus

    def GetStatus(self):
        return self.status