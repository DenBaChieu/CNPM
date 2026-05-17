from pydantic import BaseModel
from User import *
import time
import sqlite3
import secrets

SESSION_DURATION = 1800

currentSessions = {}

class LoginData(BaseModel):
    id: int
    password: str

def SetupAuthSystem():
    conn = sqlite3.connect("../Database/Login.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loginInfo (
        userId INTEGER PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

#Login
def AuthenticateUser(data: LoginData):
    conn = sqlite3.connect("../Database/Login.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loginInfo WHERE userId = ? AND password = ?", (data.id, data.password))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return None
    return GetUserFromId(data.id)

#Check if session is valid (not expired and exists)
def ValidateSession(sessionId: str) -> bool:
    if not currentSessions.get(sessionId):
        return False
    
    if time.time() > currentSessions.get(sessionId)["expiry"]:
        TerminateUserSession(sessionId)
        return False

    return True

#note: Hoan thien phan quyen theo UC6 - admin co quyen tat ca, user chi co quyen GetPaymentInfo
def AuthorizeAccess(sessionId: str, action: str) -> bool:
    #note: Kiem tra session co con hop le khong
    if not ValidateSession(sessionId):
        return False

    user: User = currentSessions.get(sessionId)["user"]
    
    #note: Admin co quyen tat ca hanh dong
    if user.role == "Admin":
        return True
    
    #note: User binh thuong chi co quyen lay thong tin thanh toan va view billing period
    allowed_actions_for_user = ["GetPaymentInfo", "ViewBillingPeriod"]
    if action in allowed_actions_for_user:
        return True
    
    #note: Staff co quyen them loai hanh dong
    if user.role == "Staff":
        staff_actions = ["WriteLog", "GetPaymentInfo"]
        if action in staff_actions:
            return True
    
    #note: Visitor chi co quyen yeu cau ve tam
    if user.role == "Visitor":
        visitor_actions = ["RequestTempTicket", "GetPaymentInfo"]
        if action in visitor_actions:
            return True
    
    return False

#Change password
def ChangePassword(userId: int, oldPassword: str, newPassword: str):
    conn = sqlite3.connect("../Database/Login.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loginInfo WHERE userId = ? AND password = ?", (userId, oldPassword))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    cursor.execute("UPDATE loginInfo SET password = ? WHERE userId = ?", (newPassword, userId))
    conn.commit()
    conn.close()
    return True

#Create new login info
def SignUp(data: LoginData):
    conn = sqlite3.connect("../Database/Login.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO loginInfo (userId, password) VALUES (?, ?)", (data.id, data.password))
    conn.commit()
    conn.close()

#Generate session token for user
def CreateUserSession(user: User) -> str:
    token = secrets.token_hex(32)
    currentSessions[token] = {"user": user, "expiry": time.time() + SESSION_DURATION}
    return token

#Delete session token to log out user
def TerminateUserSession(sessionId: str):
    del currentSessions[sessionId]

def GetUserIdFromSession(sessionId: str):
    if currentSessions[sessionId] is None:
        return None
    return currentSessions[sessionId]["user"].userId
