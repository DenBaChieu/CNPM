import datetime
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from ParkingSession import ParkingSession
from LogManager import LogManager
from User import *

#All status: Awaiting, Pending, Paid, Overdue, Invalid

def SetupBillingDB(billingManager: BillingManager):
    conn = sqlite3.connect("../Database/Billing.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        paymentId TEXT PRIMARY KEY,
        userId TEXT NOT NULL,
        amount REAL,
        paymentDate TEXT,
        dueDate TEXT,
        status TEXT,
        QRCode TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        paymentId TEXT PRIMARY KEY,
        userId TEXT NOT NULL,
        amount REAL,
        paymentDate TEXT,
        dueDate TEXT,
        status TEXT,
        QRCode TEXT
    )
    """)
    conn.commit()
    conn.close()

    billingManager.DailyCheck()
    scheduler = BackgroundScheduler()
    scheduler.add_job(billingManager.DailyCheck, 'interval', minutes=60)
    scheduler.start()

class BillingPolicy:
    pricePerHour: float = 1000
    roundUpToNextHour: bool = True
    paymentTerm: int = 30 #Days

    def __init__(self):
        pass

class BillingManager:
    billingStartTime: datetime
    billingEndTime: datetime

    def __init__(self):
        pass

    def CalculateFee(self, entryTime: datetime, exitTime: datetime) -> float:
        totalHours = (exitTime - entryTime).total_seconds() / 3600
        if BillingPolicy.roundUpToNextHour:
            totalHours = int(totalHours) + (1 if totalHours % 1 > 0 else 0)
        fee = totalHours * BillingPolicy.pricePerHour
        return fee
    
    def CalculateFee(self, totalHours: float) -> float:
        if BillingPolicy.roundUpToNextHour:
            totalHours = int(totalHours) + (1 if totalHours % 1 > 0 else 0)
        fee = totalHours * BillingPolicy.pricePerHour
        return fee

    def CalculateFee(self, parkingSession: ParkingSession) -> float:
        return self.CalculateFee(parkingSession.GetTotalTime())
    
    def GetPaymentQR(self, paymentId: str) -> str:
        return f"https://bkpay.hcmut.edu.vn/bkpay/pay?paymentId={paymentId}"

    def StartBillingPeriod(self):
        self.billingStartTime = datetime.datetime.now()

    def StopBillingPeriod(self):
        self.billingEndTime = datetime.datetime.now()
        conn = sqlite3.connect("../Database/ParkingSession.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parkingSessions WHERE sessionStatus = 'Completed' AND exitTime >= ? AND exitTime <= ?", (self.billingStartTime.isoformat(), self.billingEndTime.isoformat()))
        completedSessions = cursor.fetchall()
        for session in completedSessions:
            #If exitTime is null, skip
            if not session[2]:
                continue

            if not session[0] or not session[1] or not session[5]:
                NotifyStaff(f"Data inconsistency detected for session {session[0]}: missing required fields")
                cursor.execute("UPDATE parkingSessions SET sessionStatus = 'Invalid' WHERE sessionId = ?", (session[0],))
                continue

            entryTime = datetime.datetime.fromisoformat(session[1])
            exitTime = datetime.datetime.fromisoformat(session[2])

            if exitTime < entryTime:
                NotifyStaff(f"Data inconsistency detected for session {session[0]}: exit time is before entry time")
                cursor.execute("UPDATE parkingSessions SET sessionStatus = 'Invalid' WHERE sessionId = ?", (session[0],))
                continue

            fee = self.CalculateFee(entryTime, exitTime)
            print(f"Session {session[0]}: Fee = {fee}")
            expiresAt = (datetime.datetime.now() + datetime.timedelta(days=self.paymentTerm)).isoformat()
            if fee > 0:
                cursor.execute("INSERT INTO payment (paymentId, userId, amount, dueDate, status) VALUES (?, ?, ?, ?, ?)", (session[0], session[5], fee, expiresAt, "Awaiting"))
            else:
                cursor.execute("INSERT INTO payment (paymentId, userId, amount, paymentDate, dueDate, status) VALUES (?, ?, ?, ?, ?, ?)", (session[0], session[5], fee, datetime.datetime.now(), expiresAt, "Paid"))
                continue

            qr = self.GetPaymentQR(session[0])
            if qr is not None:
                cursor.execute("""
                                UPDATE payment 
                                SET 
                                    QRCode = ?
                                    status = 'Pending'
                                WHERE paymentId = ?
                            """, (qr, session[0]))
                NotifyUser(session[5], f"Your parking fee of {fee} is due.")

            
        conn.commit()
        conn.close()

    def ApplyOverduePolicy(self, paymentId: str):
        return

    def DailyCheck(self):
        conn = sqlite3.connect("../Database/Billing.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payment WHERE status = 'Pending' AND dueDate < ?", (datetime.datetime.now().isoformat(),))
        overduePayments = cursor.fetchall()
        for payment in overduePayments:
            cursor.execute("UPDATE payment SET status = 'Overdue' WHERE paymentId = ?", (payment[0]))
            self.ApplyOverduePolicy(payment[0])
            NotifyUser(payment[1], f"Your payment with id {payment[0]} is overdue. Please make the payment as soon as possible.")
        conn.commit()
        conn.close()

    #Debug
    def PrintAllPayments(self):
        conn = sqlite3.connect("../Database/Billing.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payment")
        payments = cursor.fetchall()
        for payment in payments:
            print(payment)
        conn.close()

    #Function for when BKPay sends a callback to notify that the payment is successful
    def VerifyPayment(self, paymentId: str):
        conn = sqlite3.connect("../Database/Billing.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE payment SET status = 'Paid', paymentDate = ? WHERE paymentId = ?", (datetime.datetime.now().isoformat(), paymentId))
        conn.commit()
        conn.close()

    #Function for when BKPay sends a callback to notify that the payment has failed
    def HandlePaymentFailure(self, paymentId: str):
        NotifyUser(paymentId, f"Your payment with id {paymentId} has failed. Please try again.")

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