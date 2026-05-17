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
        SELECT sessionId, entryTime, exitTime, userId, status
        FROM parkingSessions
        WHERE sessionStatus = 'Completed'
        AND exitTime >= ?
        AND exitTime <= ?
    """, (startTime.isoformat(), endTime.isoformat()))

    sessions = cursor.fetchall()

    user_sessions = defaultdict(list)

    for session in sessions:
        sessionId, entryTime, exitTime, userId, status = session

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

            NotifyUser(userId, f"Tổng phí gửi xe: {totalFee}")

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

def SaveTicket(ticket: Ticket):
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
    amount: float | None = None
    paymentDate: str | None = None
    dueDate: str | None = None
    status: str
    QRCode: str | None = None

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