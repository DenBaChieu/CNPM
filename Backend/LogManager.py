from datetime import datetime

class Filter:
    pass

class LogManager:
    log_file = "../Database/Log.txt"
    
    @staticmethod
    def LogEvent(event: str):
        #note: Ghi log ra console va luu vao file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {event}"
        print(log_message)
        
        try:
            with open(LogManager.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Error writing to log file: {str(e)}")

    @staticmethod
    def SearchLogs(filter: Filter):
        #note: Tim kiem log theo dieu kien (chua trien khai day du)
        pass

    @staticmethod
    def ExportLogs(format: str):
        #note: Xuat log theo format (chua trien khai day du)
        pass

    @staticmethod
    def ArchiveLogs():
        #note: Luu tru log cu (chua trien khai day du)
        pass
