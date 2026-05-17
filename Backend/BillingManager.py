from datetime import datetime, timedelta
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from ParkingSession import ParkingSession
from LogManager import LogManager
from User import *

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
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        startTime TEXT,
        endTime TEXT
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

def StopBillingPeriod():
    paymentConn = sqlite3.connect("../Database/Billing.db")
    paymentCursor = paymentConn.cursor()
    #Set up end time
    paymentCursor.execute("""
    UPDATE billing
    SET endTime = ?
    WHERE id = 1
    """, (datetime.now().isoformat(),))

    #Get start time
    paymentCursor.execute("SELECT startTime FROM billing WHERE id = 1")
    result = paymentCursor.fetchone()
    startTime = datetime.fromisoformat(result[0])

    conn = sqlite3.connect("../Database/ParkingSession.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parkingSessions WHERE sessionStatus = 'Completed' AND exitTime >= ? AND exitTime <= ?", (startTime, datetime.now().isoformat()))
    completedSessions = cursor.fetchall()
    for session in completedSessions:
        #If exitTime is null, skip
        if not session[2]:
            continue

        if not session[0] or not session[1] or not session[5]:
            NotifyStaff(f"Data inconsistency detected for session {session[0]}: missing required fields")
            cursor.execute("UPDATE parkingSessions SET sessionStatus = 'Invalid' WHERE sessionId = ?", (session[0],))
            continue

        entryTime = datetime.fromisoformat(session[1])
        exitTime = datetime.fromisoformat(session[2])

        if exitTime < entryTime:
            NotifyStaff(f"Data inconsistency detected for session {session[0]}: exit time is before entry time")
            cursor.execute("UPDATE parkingSessions SET sessionStatus = 'Invalid' WHERE sessionId = ?", (session[0],))
            continue

        fee = CalculateFeeByStartAndExit(entryTime, exitTime)
        expiresAt = (datetime.now() + timedelta(days=BillingPolicy.paymentTerm)).isoformat()
        if fee > 0:
            paymentCursor.execute("INSERT INTO payment (paymentId, userId, amount, dueDate, status) VALUES (?, ?, ?, ?, ?)", (session[0], session[5], fee, expiresAt, "Awaiting"))
        else:
            paymentCursor.execute("INSERT INTO payment (paymentId, userId, amount, paymentDate, dueDate, status) VALUES (?, ?, ?, ?, ?, ?)", (session[0], session[5], fee, datetime.now(), expiresAt, "Paid"))
            continue

        qr = GetPaymentQR(session[0])
        if qr is not None:
            paymentCursor.execute("""
                            UPDATE payment 
                            SET 
                                QRCode = ?,
                                status = 'Pending'
                            WHERE paymentId = ?
                        """, (qr, session[0]))
            NotifyUser(session[5], f"Your parking fee of {fee} is due.")

    conn.commit()
    conn.close()
    paymentConn.commit()
    paymentConn.close()

#Function for when BKPay sends a callback to notify that the payment is successful
def VerifyPayment(paymentId: str):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE payment SET status = 'Paid', paymentDate = ? WHERE paymentId = ?", (datetime.now().isoformat(), paymentId,))
    conn.commit()
    conn.close()

#Function for when BKPay sends a callback to notify that the payment has failed
def HandlePaymentFailure(paymentId: str):
    NotifyUser(paymentId, f"Your payment with id {paymentId} has failed. Please try again.")

class Payment(BaseModel):
    paymentId: str
    userId: int
    amount: float | None = None
    paymentDate: str | None = None
    dueDate: str | None = None
    status: str
    QRCode: str | None = None

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