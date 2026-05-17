import json
from LEDBoard import LEDBoard

class GuidanceEngine:
    def __init__(self, parking_manager):
        self.parking_manager = parking_manager
        self.connectedLEDs = []
        self.overrides = {} # Stores manual mock overrides

    def load_map(self, json_path: str):
        self.connectedLEDs = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            for board_data in map_data.get("led_boards", []):
                board = LEDBoard(
                    board_data["ledID"], 
                    board_data["locationNode"],
                    board_data.get("x", 50),
                    board_data.get("y", 50)
                )
                board.routes_config = board_data.get("routes", []) 
                self.connectedLEDs.append(board)
            print(f"Loaded {len(self.connectedLEDs)} LED boards.")
        except Exception as e:
            print(f"Error loading LED map: {e}")

    def _get_board(self, ledID: str):
        return next((b for b in self.connectedLEDs if b.ledID == ledID), None)

    # --- Override Methods for Mocking ---
    def set_override(self, ledID: str, arrow: str, color: str):
        if ledID not in self.overrides:
            self.overrides[ledID] = {}
        self.overrides[ledID][arrow] = color

    def clear_overrides(self):
        self.overrides = {}

    # --- Standard Math Methods ---
    def _calculate_route_stats(self, route, visited=None):
        if visited is None:
            visited = set()
        total_cap = 0
        total_avail = 0

        for child_id in route.get("target_children", []):
            if child_id in visited:
                continue 
            visited.add(child_id)
            child_board = self._get_board(child_id)
            if child_board:
                for child_route in getattr(child_board, 'routes_config', []):
                    c_cap, c_avail = self._calculate_route_stats(child_route, visited)
                    total_cap += c_cap
                    total_avail += c_avail

        for z_id in route.get("target_zones", []):
            zone = next((z for z in self.parking_manager.managedZones if z.zoneId == z_id), None)
            if zone:
                total_cap += zone.capacity
                total_avail += len(zone.GetAvailableSlots())

        target_slots = route.get("target_slots", [])
        if target_slots:
            for z in self.parking_manager.managedZones:
                for slot in z.slots:
                    if slot.slotId in target_slots:
                        total_cap += 1
                        if slot.slotStatus == "Vacant":
                            total_avail += 1
        return total_cap, total_avail

    def evaluate_capacity(self, capacity: int, available: int) -> dict:
        if capacity == 0:
            return {"color": "RED", "message": "ERROR"}
        vacancy_rate = (available / capacity) * 100
        if vacancy_rate == 0:
            return {"color": "RED", "message": "FULL"}
        elif vacancy_rate <= 30:
            return {"color": "YELLOW", "message": "ALMOST FULL"}
        else:
            return {"color": "GREEN", "message": "AVAILABLE"}

    # --- Split API Methods ---
    def update_all_leds(self):
        """FUNCTION 1: Does the math and sets the REAL physical LED hardware."""
        for led in self.connectedLEDs:
            displays = []
            for route in getattr(led, 'routes_config', []):
                arrow = route.get("arrow", "STRAIGHT")
                
                # Check for manual mock override first
                override_color = self.overrides.get(led.ledID, {}).get(arrow)
                if override_color:
                    displays.append({
                        "arrow": arrow,
                        "color": override_color,
                        "message": "OVERRIDE"
                    })
                    continue

                # If no override, do the real math
                total_capacity, total_available = self._calculate_route_stats(route)
                state = self.evaluate_capacity(total_capacity, total_available)
                displays.append({
                    "arrow": arrow,
                    "color": state["color"],
                    "message": state["message"]
                })
            
            led.updateDisplays(displays)

    def get_frontend_state(self):
        """FUNCTION 2: Generates the dynamic JSON purely for the Frontend UI."""
        status_report = []
        for led in self.connectedLEDs:
            status_report.append({
                "ledID": led.ledID,
                "location": led.locationNode,
                "x": led.x,
                "y": led.y,
                "status": led.connectionStatus,
                "displays": led.displays
            })
        return status_report