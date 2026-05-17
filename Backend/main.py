from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from AuthManager import *
from BillingManager import *
from ParkingManager import ParkingManager
from ParkingZone import ParkingZone
from LogManager import LogManager
from ParkingSession import *
from User import *
from Vehicle import *
from ParkingSlot import ParkingSlot
from Sensor import Sensor
from LEDBoard import LEDBoard
from GuidanceEngine import GuidanceEngine

import uvicorn
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SetupAuthSystem()
SetupUserSystem()
SetupParkingSessionDB()
SetupVehicleDB()
SetupBillingDB()
try:
    CreateAccount(0, "Admin", "Admin", "", "")
except Exception as e:
    print("Admin account already exists")

try:
    SignUp(LoginData(id=0, password="Admin"))
except Exception as e:
    print("Admin login already exists")

#Create parking zones and slots
parkingManager = ParkingManager()

parkingSlots = []
parkingSensors = []
tickets: list[Ticket] = []
zones = ["CS1", "CS2"]
for zoneName in zones:
    slots = []
    for i in range(1, 151):
        sensor = Sensor(sensorId=f"{zoneName}-Sensor{i}")
        slotType = "Car" if i > 100 else "Motorcycle"
        slot = ParkingSlot(slotId=f"{zoneName}-Slot{i}", slotType=slotType, sensor=sensor, StartParkingSession=parkingManager.StartParkingSession, StopParkingSession=parkingManager.StopParkingSession)
        slots.append(slot)
        parkingSlots.append(slot)
        parkingSensors.append(sensor)
        print("Sensor id: ", sensor.sensorId)
    zone = ParkingZone(zoneId=zoneName, zoneName=zoneName, slots=slots)
    parkingManager.managedZones.append(zone)

#Initialize Guidance Engine and load the visual map
guidanceEngine = GuidanceEngine(parking_manager=parkingManager)
guidanceEngine.load_map("led_map.json")

print("Parking zones and slots initialized")

#---------- Payment ----------#
@app.get("/payment/getInfo")
def GetInfo(authorization: str = Header()):
    if not AuthorizeAccess(authorization.replace("Bearer ", ""), "GetPaymentInfo"):
        raise HTTPException(status_code=403, detail="Unauthorized")

    userId = GetUserIdFromSession(authorization.replace("Bearer ", ""))
    if userId is not None:
        print(GetPayments(userId=userId))
        return GetPayments(userId=userId)
    else:
        raise HTTPException(status_code=403, detail="No user ID found")
    
@app.post("/payment/startBillingPeriod")
def StartBillingPeriodAPI(authorization: str = Header()):
    if not AuthorizeAccess(authorization.replace("Bearer ", ""), "StartBillingPeriod"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    StartBillingPeriod()
    return {"message": "Successful"}
    
@app.post("/payment/stopBillingPeriod")
def StopBillingPeriodAPI(authorization: str = Header()):
    if not AuthorizeAccess(authorization.replace("Bearer ", ""), "StopBillingPeriod"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    StopBillingPeriod()
    return {"message": "Successful"}

@app.post("/payment/pay")
def Pay(data: PayRequest):
    VerifyPayment(data.paymentId)

@app.post("/ticket/pay")
def Pay(data: PayRequest):
    VerifyTicketPayment(data.paymentId)

#---------- Authentication ----------#
@app.post("/login")
def Login(data: LoginData):
    user = AuthenticateUser(data)
    if user is not None:
        token = CreateUserSession(user)
        return {"message": "Login successful", "role": user.role, "token": token}
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
@app.post("/logout")
def Logout(sessionId: str):
    if ValidateSession(sessionId):
        TerminateUserSession(sessionId)
        return {"message": "Logout successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid session")
    
@app.get("/validateSession")
def ValidateUserSession(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    if ValidateSession(token):
        return {"message": "Session is valid"}
    else:
        raise HTTPException(status_code=401, detail="Invalid session")

#---------- Sensors ----------#
@app.post("/sensor/detect")
def UpdateSensor(input: dict):
    sensorId = input.get("sensorId", "")
    licensePlate = input.get("licensePlate")
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        if licensePlate:
            user, vehicle = parkingManager.GetZoneFromSensor(sensor=sensor).GetUserAndVehicleInZone(licensePlate)
            if user is None or vehicle is None:
                raise HTTPException(status_code=404, detail="Entry not found")

        sensor.DetectVehicle(licensePlate)
        return {"message": "Sensor updated"}
    else:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
@app.post("/sensor/failure")
def ReportSensorFailure(sensorId: str):
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        sensor.ReportFailure()
        return {"message": "Sensor reported as failed"}
    else:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
@app.post("/sensor/reconnect")
def ReconnectSensor(sensorId: str):
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        sensor.Reconnect()
        return {"message": "Sensor reconnected"}
    else:
        raise HTTPException(status_code=404, detail="Sensor not found")

@app.get("/parking/getAvailableSlots")
def GetAvailableSlots(zoneId: str):
    zone = next((z for z in parkingManager.managedZones if z.zoneId == zoneId), None)
    if zone:
        availableSlots = zone.GetAvailableSlots()
        return {"availableSlots": [slot.slotId for slot in availableSlots]}
    else:
        raise HTTPException(status_code=404, detail="Parking zone not found")

@app.post("/sensor/studentEnter")
def StudentEnter(data: dict):
    studentId = data.get("id")
    licensePlate = data.get("licensePlate")
    zoneId = data.get("zoneId")
    if studentId is None or licensePlate is None or zoneId is None or license == "":
        raise HTTPException(status_code=400, detail="Missing data")
    
    studentId = int(studentId)
    
    user = GetUserFromId(studentId)
    if user is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    zone = parkingManager.GetZone(zoneId)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")

    vehicle = GetVehicle(licensePlate)

    zone.UserEntered(user, vehicle)

@app.post("/sensor/exit")
def Exit(data: dict):
    licensePlate = data.get("licensePlate")
    zoneId = data.get("zoneId")
    if licensePlate is None or zoneId is None:
        raise HTTPException(status_code=400, detail="Missing data")
    
    zone = parkingManager.GetZone(zoneId)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    if zone.VehicleLeft(licensePlate=licensePlate):
        parkingTicket = None
        for ticket in tickets:
            if ticket.licensePlate == licensePlate:
                ticket.CloseTicket()
                parkingTicket = ticket
                break 

        if parkingTicket:
            return {"message": "Success", "ticket": ticket.GenerateRecord()}
        else:
            return {"message": "Success"}
    else:
        raise HTTPException(status_code=404, detail="Vehicle entry not found")
    
#---------- Guidance Engine (UC04) ----------#
@app.get("/guidance/status")
def GetGuidanceStatus():
    """Endpoint for the Frontend React Dashboard to consume"""
    # 1. Update the physical hardware states based on live IoT data
    guidanceEngine.update_all_leds()
    
    # 2. Return the pure dynamic JSON state to the frontend
    dynamic_json = guidanceEngine.get_frontend_state()
    return {"led_boards": dynamic_json}

#---------- Mock Engine (UC04 Testing) ----------#
@app.post("/mock/led")
def MockLEDOverride(input: dict):
    """
    Directly force an LED to a specific color.
    POST JSON: {"ledID": "BOARD_JUNCTION_1", "arrow": "LEFT", "color": "RED"}
    Send color: "CLEAR" to remove all overrides and return to normal math.
    """
    ledID = input.get("ledID")
    arrow = input.get("arrow", "STRAIGHT")
    color = input.get("color")

    if not ledID or not color:
        return {"message": "Missing ledID or color"}, 400

    if color.upper() == "CLEAR":
        guidanceEngine.clear_overrides()
        return {"message": "All overrides cleared. Returning to real math."}
    else:
        guidanceEngine.set_override(ledID, arrow, color.upper())
        return {"message": f"Forced {ledID} [{arrow}] to {color.upper()}"}

#---------- Admin ----------#

#Admin creates all accounts including students and staffs
@app.post("/createaccount")
def CreateAccountAPI(data: CreateAccountData, authorization: str = Header()):
    if not AuthorizeAccess(authorization.replace("Bearer ", ""), "CreateAccount"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    CreateAccount(
        userId=data.userId,
        fullName=data.fullName,
        role=data.role,
        email=data.email,
        phoneNumber=data.phoneNumber
    )

    SignUp(
        LoginData(
            id=data.userId,
            password=data.password
        )
    )

    return {"message": "Signup successful"}

#Admin creates all registered vehicles
@app.post("/registerVehicle")
def CreateAccountAPI(data: CreateVehicleData, authorization: str = Header()):
    if not AuthorizeAccess(authorization.replace("Bearer ", ""), "CreateVehicle"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    RegisterVehicle(data.licensePlate, data.vehicleType, data.ownerId)

    return {"message": "Register successful"}

#---------- TemporaryTicket ----------#
@app.post("/visitor/requestTempTicket")
def RequestTempTicket(data: dict):
    licensePlate = data.get("licensePlate")
    zoneId = data.get("zoneId")
    zone = parkingManager.GetZone(zoneId)
    if zone is None:
        raise HTTPException(status_code=404, detail="Parking zone not found")

    available_slots = zone.GetAvailableSlots()
    if len(available_slots) == 0:
        raise HTTPException(status_code=400, detail="No available slots in this zone")

    user = Visitor()
    vehicle = GetVehicle(licensePlate)
    zone.UserEntered(user, vehicle)

    ticket = Ticket(zoneId=zoneId, licensePlate=licensePlate)
    tickets.append(ticket)

    LogManager.LogEvent(f"Temporary ticket {ticket.ticketId} issued for {licensePlate} at zone {zoneId}")

    return {
        "message": "Temporary ticket issued successfully",
        "ticket": ticket.GenerateRecord()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)