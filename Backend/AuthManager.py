from pydantic import BaseModel
from User import *
import time

SESSION_DURATION = 1800

currentSessions = {}

class LoginData(BaseModel):
    id: str
    password: str

#Basically login
def AuthenticateUser(data: LoginData):
    #TODO: Finish
    return Student(
            userId=data.id,
            fullName="John Doe",
            role="Student",
            email="",
            phoneNumber="1234567890",
            accumulatedFees=0.0
        )

def ValidateSession(sessionId: str) -> bool:
    if not currentSessions.get(sessionId):
        return False
    
    if time.time() > currentSessions.get(sessionId)["expiry"]:
        TerminateUserSession(sessionId)
        return False

    return True

def AuthorizeAccess(sessionId: str, action: str) -> bool:
    #TODO: Finish

    #No system to make the user login again yet so we will just not allow them
    if not ValidateSession(sessionId):
        return False

    user: User = currentSessions.get(sessionId)["user"]
    if user.role == "Admin":
        return True
    else:
        return True

def SignUp(data: LoginData):
    pass

def Logout(userId: str):
    pass

def CreateUserSession(user: User) -> str:
    #TODO: Finish
    currentSessions["dummy-session-id"] = {"user": user, "expiry": time.time() + SESSION_DURATION}
    return "dummy-session-id"

def TerminateUserSession(sessionId: str):
    del currentSessions[sessionId]

def GetUserIdFromSession(sessionId: str):
    pass