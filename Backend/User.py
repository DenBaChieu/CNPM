from LogManager import LogManager
from pydantic import BaseModel
import sqlite3

class CreateAccountData(BaseModel):
    userId: int
    fullName: str
    role: str
    email: str
    phoneNumber: str
    password: str

class User:
    userId: int
    fullName: str
    role: str
    email: str
    phoneNumber: str

    def __init__(self, userId: int, fullName: str, role: str, email: str, phoneNumber: str):
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
    def WriteLog(event: str):
        LogManager.LogEvent(event)

    def CreateTicket():
        pass

class Student(User):
    accumulatedFees: float

    def __init__(self, userId: str, fullName: str, role: str, email: str, phoneNumber: str, accumulatedFees: float):
        super().__init__(userId, fullName, role, email, phoneNumber)
        self.accumulatedFees = accumulatedFees

def NotifyStaff(message: str):
    pass

def NotifyUser(userId: int, message: str):
    pass

def CreateAccount(userId: int, fullName: str, role: str, email: str, phoneNumber: str):
    conn = sqlite3.connect("../Database/User.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user (userId, fullName, role, email, phoneNumber) VALUES (?, ?, ?, ?, ?)", (userId, fullName, role, email, phoneNumber))

    if role == "Student":
        cursor.execute("INSERT INTO student (userId, accumulatedFees) VALUES (?, ?)", (userId, 0.0))
    elif role == "Admin":
        cursor.execute("INSERT INTO admin (userId, adminLevel, managedAreas) VALUES (?, ?, ?)", (userId, 1, ""))

    conn.commit()
    conn.close()

def SetupUserSystem():
    conn = sqlite3.connect("../Database/User.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        userId INTEGER PRIMARY KEY,
        fullName TEXT,
        role TEXT,
        email TEXT,
        phoneNumber TEXT
    );
    """)       
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        userId INTEGER PRIMARY KEY,
        adminLevel INTEGER,
        managedAreas TEXT,
        FOREIGN KEY(userId) REFERENCES user(userId)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        userId INTEGER PRIMARY KEY,
        accumulatedFees REAL,
        FOREIGN KEY(userId) REFERENCES user(userId)
    );
    """)

    conn.commit()
    conn.close()

def GetUserFromId(userId: int) -> User:
    conn = sqlite3.connect("../Database/User.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE userId = ?", (userId,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return None
    
    return User(
        userId=result[0],
        fullName=result[1],
        role=result[2],
        email=result[3],
        phoneNumber=result[4]
    )