class User:
    userId: str
    fullName: str
    role: str
    email: str
    phoneNumber: str

    def __init__(self, userId: str, fullName: str, role: str, email: str, phoneNumber: str):
        self.userId = userId
        self.fullName = fullName
        self.role = role
        self.email = email
        self.phoneNumber = phoneNumber
    
    def UpdateProfile(self, fullName: str, email: str, phoneNumber: str):
        self.fullName = fullName
        self.email = email
        self.phoneNumber = phoneNumber

class Admin(User):
    adminLevel: int
    managedAreas: list

    def __init__(self, userId: str, fullName: str, role: str, email: str, phoneNumber: str, adminLevel: int, managedAreas: list):
        super().__init__(userId, fullName, role, email, phoneNumber)
        self.adminLevel = adminLevel
        self.managedAreas = managedAreas

    def CreateUser():
        pass

    def DeleteUser():
        pass

    def UpdateUser():
        pass

    def ViewLogs():
        pass

    def GenerateReport():
        pass
    
class Visitor(User):
    def RequestTicket():
        pass

class Staff(User):
    def WriteLog():
        pass

    def CreateTicket():
        pass

class Student(User):
    accumulatedFees: float

    def __init__(self, userId: str, fullName: str, role: str, email: str, phoneNumber: str, accumulatedFees: float):
        super().__init__(userId, fullName, role, email, phoneNumber)
        self.accumulatedFees = accumulatedFees