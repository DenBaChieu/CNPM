from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from AuthManager import *
from ParkingManager import ParkingManager
from ParkingZone import ParkingZone
from LogManager import LogManager
from User import User
from Vehicle import Vehicle
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

#Create parking zones and slots
parkingManager = ParkingManager()
parkingSlots = []
parkingSensors = []
for zoneName in ["CS1", "CS2"]:
    slots = []
    for i in range(1, 150):
        sensor = Sensor(sensorId=f"{zoneName}-Sensor{i}")
        slotType = "Car" if i % 2 == 0 else "Motorcycle"
        slot = ParkingSlot(slotId=f"{zoneName}-Slot{i}", slotType=slotType, sensor=sensor, GetVehicle=parkingManager.GetVehicle, StartParkingSession=parkingManager.StartParkingSession, StopParkingSession=parkingManager.StopParkingSession)
        slots.append(slot)
        parkingSlots.append(slot)
        parkingSensors.append(sensor)
        print("Sensor id: ", sensor.sensorId)
    zone = ParkingZone(zoneId=zoneName, zoneName=zoneName, slots=slots)
    parkingManager.managedZones.append(zone)

print("Parking zones and slots initialized")

# _ Initialize Guidance Engine and load the visual map
guidanceEngine = GuidanceEngine(parking_manager=parkingManager)
guidanceEngine.load_map("led_map.json")

#---------- Authentication ----------#
@app.post("/login")
def Login(data: LoginData):
    user = AuthenticateUser(data)
    if user:
        token = CreateUserSession(user.userId)
        return {"message": "Login successful", "role": user.role, "token": token}
    else:
        return {"message": "Invalid credentials"}, 401
    
@app.post("/signup")
def SignUp(data: LoginData):
    if SignUp(data):
        return {"message": "Signup successful"}
    
@app.post("/logout")
def Logout(sessionId: str):
    if ValidateSession(sessionId):
        TerminateUserSession(sessionId)
        return {"message": "Logout successful"}
    else:
        return {"message": "Invalid session"}, 401
    
@app.get("/validateSession")
def ValidateUserSession(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    if ValidateSession(token):
        return {"message": "Session is valid"}
    else:
        return {"message": "Invalid session"}, 401

#---------- Sensors ----------#
@app.post("/sensor/detect")
def UpdateSensor(input: dict):
    sensorId = input.get("sensorId", "")
    licensePlate = input.get("licensePlate")
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        sensor.DetectVehicle(licensePlate)
        return {"message": "Sensor updated"}
    else:
        return {"message": "Sensor not found"}, 404
    
@app.post("/sensor/failure")
def ReportSensorFailure(sensorId: str):
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        sensor.ReportFailure()
        return {"message": "Sensor reported as failed"}
    else:
        return {"message": "Sensor not found"}, 404
    
@app.post("/sensor/reconnect")
def ReconnectSensor(sensorId: str):
    sensor = next((s for s in parkingSensors if s.sensorId == sensorId), None)
    if sensor:
        sensor.Reconnect()
        return {"message": "Sensor reconnected"}
    else:
        return {"message": "Sensor not found"}, 404

@app.get("/parking/getAvailableSlots")
def GetAvailableSlots(zoneId: str):
    zone = next((z for z in parkingManager.managedZones if z.zoneId == zoneId), None)
    if zone:
        availableSlots = zone.GetAvailableSlots()
        return {"availableSlots": [slot.slotId for slot in availableSlots]}
    else:
        return {"message": "Parking zone not found"}, 404
    
# _ Guidance Engine (UC04)
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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)