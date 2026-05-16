class LEDBoard:
    def __init__(self, ledID: str, locationNode: str, x: float, y: float):
        self.ledID = ledID
        self.locationNode = locationNode
        self.x = x
        self.y = y
        self.connectionStatus = "ONLINE"
        # Since one board can show multiple arrows (Left, Right, Straight)
        self.displays = [] 

    def updateDisplays(self, new_displays: list):
        self.displays = new_displays

    def triggerMaintenanceMode(self):
        self.connectionStatus = "OFFLINE"
        self.displays = [{
            "arrow": "ALL",
            "color": "YELLOW",
            "message": "Đang bảo trì",
            "available": 0,
            "capacity": 0
        }]