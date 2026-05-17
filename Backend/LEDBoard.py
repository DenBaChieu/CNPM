class LEDBoard:
    def __init__(self, ledID: str, locationNode: str, x: float, y: float):
        self.ledID = ledID
        self.locationNode = locationNode
        self.x = x
        self.y = y
        self.connectionStatus = "ONLINE"
        # Represents the actual lights currently glowing on the physical board
        self.displays = [] 

    def updateDisplays(self, new_displays: list):
        """Hardware command to change the physical LED lights"""
        self.displays = new_displays

    def triggerMaintenanceMode(self):
        self.connectionStatus = "OFFLINE"
        self.displays = [{
            "arrow": "ALL",
            "color": "YELLOW",
            "message": "MAINTENANCE"
        }]