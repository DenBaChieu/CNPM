from datetime import datetime, timedelta
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from ParkingSession import ParkingSession
from LogManager import LogManager
from User import *
from collections import defaultdict
import secrets

#All status: Awaiting, Pending, Paid, Overdue, Invalid

class PayRequest(BaseModel):
    paymentId: str

def SetupBillingDB():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        paymentId TEXT PRIMARY KEY,
        userId INT NOT NULL,
        amount REAL,
        paymentDate TEXT,
        dueDate TEXT,
        status TEXT,
        QRCode TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticket (
        ticketId TEXT PRIMARY KEY,
        licensePlate TEXT NOT NULL,
        zoneId TEXT,
        amount REAL,
        issuedTime TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        startTime TEXT,
        endTime TEXT
    )
    """)

    #note: Them bang billing_policy de luu cau hinh bieu phi theo UC6
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing_policy (
        policyId TEXT PRIMARY KEY,
        groupTarget TEXT,
        priceType TEXT,
        priceValue REAL,
        startDate TEXT,
        endDate TEXT,
        isActive BOOLEAN,
        createdDate TEXT,
        updatedDate TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO billing (id, startTime, endTime)
    VALUES (1, NULL, NULL)
    """)

    conn.commit()
    conn.close()

    DailyCheck()
    scheduler = BackgroundScheduler()
    scheduler.add_job(DailyCheck, 'interval', minutes=60)
    scheduler.start()

def ApplyOverduePolicy(paymentId: str):
    return

def DailyCheck():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payment WHERE status = 'Pending' AND dueDate < ?", (datetime.now().isoformat(),))
    overduePayments = cursor.fetchall()
    for payment in overduePayments:
        cursor.execute("UPDATE payment SET status = 'Overdue' WHERE paymentId = ?", (payment[0],))
        ApplyOverduePolicy(payment[0])
        NotifyUser(payment[1], f"Your payment with id {payment[0]} is overdue. Please make the payment as soon as possible.")
    conn.commit()
    conn.close()

#Debug
def PrintAllPayments():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payment")
    payments = cursor.fetchall()
    for payment in payments:
        print(payment)
    conn.close()

#note: Ham lay cau hinh bieu phi dang hoat dong theo nhom doi tuong
def GetActiveBillingPolicy(groupTarget: str = None):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    if groupTarget:
        cursor.execute("SELECT * FROM billing_policy WHERE isActive = 1 AND groupTarget = ? AND startDate <= ? AND endDate >= ? ORDER BY updatedDate DESC LIMIT 1", (groupTarget, now, now))
    else:
        cursor.execute("SELECT * FROM billing_policy WHERE isActive = 1 AND startDate <= ? AND endDate >= ? ORDER BY updatedDate DESC LIMIT 1", (now, now))
    
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"policyId": result[0], "groupTarget": result[1], "priceType": result[2], "priceValue": result[3]}
    return None

#note: Ham tao hoac cap nhat cau hinh bieu phi (admin goi)
def CreateOrUpdateBillingPolicy(policy_dict: dict):
    try:
        conn = sqlite3.connect("../Database/Billing.db")
        cursor = conn.cursor()
        policyId = policy_dict.get("policyId") or secrets.token_hex(16)
        
        cursor.execute("INSERT OR REPLACE INTO billing_policy (policyId, groupTarget, priceType, priceValue, startDate, endDate, isActive, createdDate, updatedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (policyId, policy_dict.get("groupTarget"), policy_dict.get("priceType"), policy_dict.get("priceValue"), policy_dict.get("startDate"), policy_dict.get("endDate"), 1 if policy_dict.get("isActive") else 0, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        LogManager.LogEvent(f"Billing policy updated: {policy_dict.get('groupTarget')} - {policy_dict.get('priceType')} - {policy_dict.get('priceValue')}")
        return {"policyId": policyId, "status": "success"}
    except Exception as e:
        LogManager.LogEvent(f"Error updating billing policy: {str(e)}")
        return {"status": "error", "message": str(e)}

#note: Ham lay tat ca cau hinh bieu phi
def GetAllBillingPolicies():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT policyId, groupTarget, priceType, priceValue, startDate, endDate, isActive FROM billing_policy ORDER BY updatedDate DESC")
    policies = cursor.fetchall()
    conn.close()
    result = []
    for p in policies:
        result.append({"policyId": p[0], "groupTarget": p[1], "priceType": p[2], "priceValue": p[3], "startDate": p[4], "endDate": p[5], "isActive": bool(p[6])})
    return result

#note: Ham lay chu ky thanh toan hien tai
def GetCurrentBillingPeriod():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT startTime, endTime FROM billing WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"startTime": result[0], "endTime": result[1]}
    return {"startTime": None, "endTime": None}

def GetPayments(userId: int, amount: int = 0) -> list:
    result = []
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payment WHERE userId = ?", (userId,))
    payments = cursor.fetchall()
    for payment in payments:
        result.append(Payment(
            paymentId=payment[0],
            userId=payment[1],
            amount=payment[2],
            paymentDate=payment[3],
            dueDate=payment[4],
            status=payment[5],
            QRCode=payment[6],
        ))
    conn.commit()
    conn.close()
    return result

#note: Model cau hinh bieu phi theo UC6 - admin co the thay doi gia, loai phi, nhom doi tuong
class BillingPolicyModel(BaseModel):
    policyId: str = None
    groupTarget: str  # "Student", "Visitor", "Staff"
    priceType: str    # "hourly", "per_turn"
    priceValue: float
    startDate: str
    endDate: str
    isActive: bool = True

class BillingPolicy:
    pricePerHour: float = 1000
    roundUpToNextHour: bool = True
    paymentTerm: int = 30 #Days

    def __init__(self):
        pass

def CalculateFeeByStartAndExit(entryTime: datetime, exitTime: datetime) -> float:
    totalHours = (exitTime - entryTime).total_seconds() / 3600
    if BillingPolicy.roundUpToNextHour:
        totalHours = int(totalHours) + (1 if totalHours % 1 > 0 else 0)
    fee = totalHours * BillingPolicy.pricePerHour
    return fee

def CalculateFeeByTotalHours(totalHours: float) -> float:
    if BillingPolicy.roundUpToNextHour:
        totalHours = int(totalHours) + (1 if totalHours % 1 > 0 else 0)
    fee = totalHours * BillingPolicy.pricePerHour
    return fee

def CalculateFeeByParkingSession(parkingSession: ParkingSession) -> float:
    return CalculateFeeByTotalHours(parkingSession.GetTotalTime())

def GetPaymentQR(paymentId: str) -> str:
    return f"https://bkpay.hcmut.edu.vn/bkpay/pay?paymentId={paymentId}"

def StartBillingPeriod():
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE billing
    SET startTime = ?
    WHERE id = 1
    """, (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    #note: Ghi log khi admin bat dau chu ky thanh toan
    LogManager.LogEvent("Billing period started")

def StopBillingPeriod():
    paymentConn = sqlite3.connect("../Database/Billing.db")
    paymentCursor = paymentConn.cursor()

    #Set end time
    endTime = datetime.now()
    paymentCursor.execute("""
        UPDATE billing
        SET endTime = ?
        WHERE id = 1
    """, (endTime.isoformat(),))

    #Get start time
    paymentCursor.execute("SELECT startTime FROM billing WHERE id = 1")
    result = paymentCursor.fetchone()
    startTime = datetime.fromisoformat(result[0])

    conn = sqlite3.connect("../Database/ParkingSession.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sessionId, entryTime, exitTime, userId, sessionStatus
        FROM parkingSessions
        WHERE sessionStatus = 'Completed'
        AND exitTime >= ?
        AND exitTime <= ?
    """, (startTime.isoformat(), endTime.isoformat()))

    sessions = cursor.fetchall()

    user_sessions = defaultdict(list)

    for session in sessions:
        sessionId, entryTime, exitTime, userId, sessionStatus = session

        if not exitTime:
            continue

        entryTime = datetime.fromisoformat(entryTime)
        exitTime = datetime.fromisoformat(exitTime)

        if exitTime < entryTime:
            cursor.execute(
                "UPDATE parkingSessions SET sessionStatus = 'Invalid' WHERE sessionId = ?",
                (sessionId,)
            )
            continue

        fee = CalculateFeeByStartAndExit(entryTime, exitTime)

        user_sessions[userId].append({
            "sessionId": sessionId,
            "fee": fee
        })


    for userId, items in user_sessions.items():

        totalFee = sum(item["fee"] for item in items)
        paymentId = secrets.token_hex(16)

        expiresAt = (datetime.now() + timedelta(days=BillingPolicy.paymentTerm)).isoformat()

        if totalFee > 0:
            paymentCursor.execute("""
                INSERT INTO payment (paymentId, userId, amount, dueDate, status)
                VALUES (?, ?, ?, ?, ?)
            """, (paymentId, userId, totalFee, expiresAt, "Awaiting"))

            qr = GetPaymentQR(paymentId)

            if qr:
                paymentCursor.execute("""
                    UPDATE payment
                    SET QRCode = ?, status = 'Pending'
                    WHERE paymentId = ?
                """, (qr, paymentId))

            for item in items:
                cursor.execute("""
                    UPDATE parkingSessions
                    SET paymentId = ?
                    WHERE sessionId = ?
                """, (paymentId, item["sessionId"]))

            NotifyUser(userId, f"Tong phi gui xe: {totalFee}")

        else:
            #Free is counted as paid
            paymentCursor.execute("""
                INSERT INTO payment (paymentId, userId, amount, paymentDate, dueDate, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                paymentId,
                userId,
                0,
                endTime.isoformat(),
                expiresAt,
                "Paid"
            ))

            for item in items:
                cursor.execute("""
                    UPDATE parkingSessions
                    SET paymentId = ?
                    WHERE sessionId = ?
                """, (paymentId, item["sessionId"]))

    conn.commit()
    conn.close()
    paymentConn.commit()
    paymentConn.close()
    #note: Ghi log khi admin ket thuc chu ky thanh toan
    LogManager.LogEvent("Billing period stopped")

#Function for when BKPay sends a callback to notify that the payment is successful
def VerifyPayment(paymentId: str):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE payment SET status = 'Paid', paymentDate = ? WHERE paymentId = ?", (datetime.now().isoformat(), paymentId,))
    conn.commit()
    conn.close()

#Function for when staff collected the payment from the visitor
def VerifyTicketPayment(ticketId: str):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ticket
        SET status = 'Paid'
        WHERE ticketId = ?
    """, (ticketId,))

    conn.commit()
    conn.close()


#Function for when BKPay sends a callback to notify that the payment has failed
def HandlePaymentFailure(paymentId: str):
    NotifyUser(paymentId, f"Your payment with id {paymentId} has failed. Please try again.")

def SaveTicket(ticket):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ticket (
            ticketId, licensePlate, zoneId,
            amount, issuedTime, status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket.ticketId,
        ticket.licensePlate,
        ticket.zoneId,
        ticket.amount,
        ticket.issuedTime.isoformat(),
        ticket.status,
    ))

    conn.commit()
    conn.close()

class Payment(BaseModel):
    paymentId: str
    userId: int
    amount: float = None
    paymentDate: str = None
    dueDate: str = None
    status: str
    QRCode: str = None

class Ticket:
    ticketId: str
    amount: float
    issuedTime: datetime
    status: str
    zoneId: str
    licensePlate: str

    def __init__(self, zoneId: str, licensePlate: str):
        self.ticketId = secrets.token_hex(16)
        self.issuedTime = datetime.now()
        self.status = "Opened"
        self.zoneId = zoneId
        self.licensePlate = licensePlate
        self.amount = 0.0

    def CloseTicket(self):
        conn = sqlite3.connect("../Database/ParkingSession.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT entryTime, exitTime
            FROM parkingSessions
            WHERE licensePlate = ?
            AND sessionStatus = 'Completed'
            AND entryTime >= ?
        """, (self.licensePlate, self.issuedTime.isoformat()))

        sessions = cursor.fetchall()
        conn.close()

        total = 0.0

        for entryTime, exitTime in sessions:
            if not entryTime or not exitTime:
                continue

            entry_dt = datetime.fromisoformat(entryTime)
            exit_dt = datetime.fromisoformat(exitTime)

            if exit_dt < entry_dt:
                continue

            total += CalculateFeeByStartAndExit(entry_dt, exit_dt)

        self.amount = total
        self.status = "Pending"

        conn = sqlite3.connect("../Database/Billing.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ticket
            SET amount = ?, status = ?
            WHERE ticketId = ?
        """, (self.amount, self.status, self.ticketId))

        conn.commit()
        conn.close()

        return self.amount

    def UpdateStatus(self, newStatus: str):
        self.status = newStatus

    def GetStatus(self):
        return self.status
    
    def GenerateRecord(self):
        return {
            "ticketId": self.ticketId,
            "amount": self.amount,
            "issuedTime": self.issuedTime.isoformat() if self.issuedTime else None,
            "status": self.status,
            "zoneId": self.zoneId,
            "licensePlate": self.licensePlate,
        }
