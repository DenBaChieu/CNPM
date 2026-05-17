import sqlite3
from datetime import datetime, timedelta
import json
import csv
import os

class Filter:
    def __init__(self, keyword: str = None, startTime: datetime = None, endTime: datetime = None):
        self.keyword = keyword
        self.startTime = startTime
        self.endTime = endTime

class LogManager:

    DB_PATH = "../Database/Logs.db"

    @staticmethod
    def SetupDB():
        conn = sqlite3.connect(LogManager.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def LogEvent(event: str):
        conn = sqlite3.connect(LogManager.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO logs (event, timestamp)
            VALUES (?, ?)
        """, (event, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print(f"[LOG] {event}")

    @staticmethod
    def SearchLogs(filter: Filter):
        conn = sqlite3.connect(LogManager.DB_PATH)
        cursor = conn.cursor()

        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if filter.keyword:
            query += " AND event LIKE ?"
            params.append(f"%{filter.keyword}%")

        if filter.startTime:
            query += " AND timestamp >= ?"
            params.append(filter.startTime.isoformat())

        if filter.endTime:
            query += " AND timestamp <= ?"
            params.append(filter.endTime.isoformat())

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        conn.close()

        formatted = []

        for row in results:
            formatted.append({
                "id": row[0],
                "event": row[1],
                "timestamp": row[2]
            })

        return formatted

    @staticmethod
    def ExportLogs(format: str):
        conn = sqlite3.connect(LogManager.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()

        if format.lower() == "json":
            data = [
                {"id": r[0], "event": r[1], "timestamp": r[2]}
                for r in logs
            ]

            with open("logs_export.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return "Exported to logs_export.json"

        elif format.lower() == "csv":
            with open("logs_export.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "event", "timestamp"])
                writer.writerows(logs)

            return "Exported to logs_export.csv"

        return "Unsupported format"

    @staticmethod
    def ArchiveLogs(days: int = 7):
        cutoff = datetime.now() - timedelta(days=days)

        conn = sqlite3.connect(LogManager.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM logs WHERE timestamp < ?
        """, (cutoff.isoformat(),))

        old_logs = cursor.fetchall()

        if not old_logs:
            conn.close()
            return "No logs to archive"

        archive_file = f"logs_archive_{datetime.now().date()}.json"

        data = [
            {"id": r[0], "event": r[1], "timestamp": r[2]}
            for r in old_logs
        ]

        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        # Delete from DB
        cursor.execute("""
            DELETE FROM logs WHERE timestamp < ?
        """, (cutoff.isoformat(),))

        conn.commit()
        conn.close()

        return f"Archived {len(old_logs)} logs"