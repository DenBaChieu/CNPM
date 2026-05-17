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

#Check if user has access to perform the action
def AuthorizeAccess(sessionId: str, action: str) -> bool:
    #TODO: Finish

    #No system to make the user login again yet so we will just not allow them
    if not ValidateSession(sessionId):
        return False

    user: User = currentSessions.get(sessionId)["user"]
    if user.role == "Admin":
        return True
    elif action == "GetPaymentInfo":
        return True
    else:
        return True

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