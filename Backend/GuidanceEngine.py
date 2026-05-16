import json
from LEDBoard import LEDBoard

class GuidanceEngine:
    def __init__(self, parking_manager):
        self.parking_manager = parking_manager
        self.connectedLEDs = []

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
            print(f"Loaded {len(self.connectedLEDs)} LED boards (Recursive Bottom-Up Mode).")
        except Exception as e:
            print(f"Error loading LED map: {e}")

    def _get_board(self, ledID: str):
        return next((b for b in self.connectedLEDs if b.ledID == ledID), None)

    def _calculate_route_stats(self, route, visited=None):
        """
        Đệ quy duyệt cây Bottom-Up. 
        Nếu là Node Cha -> Lấy tổng của các Node Con.
        Nếu là Node Lá -> Lấy dữ liệu Slot thực tế từ IoT ParkingManager.
        """
        if visited is None:
            visited = set()

        total_cap = 0
        total_avail = 0

        # 1. Gọi đệ quy xuống các bảng con (Children)
        for child_id in route.get("target_children", []):
            if child_id in visited:
                continue # Chống loop vô hạn nếu JSON bị config vòng tròn
            visited.add(child_id)
            
            child_board = self._get_board(child_id)
            if child_board:
                for child_route in getattr(child_board, 'routes_config', []):
                    c_cap, c_avail = self._calculate_route_stats(child_route, visited)
                    total_cap += c_cap
                    total_avail += c_avail

        # 2. Đếm trực tiếp nếu là Node Lá (quản lý theo Zone)
        for z_id in route.get("target_zones", []):
            zone = next((z for z in self.parking_manager.managedZones if z.zoneId == z_id), None)
            if zone:
                total_cap += zone.capacity
                total_avail += len(zone.GetAvailableSlots())

        # 3. Đếm trực tiếp nếu là Node Lá (quản lý theo từng Slot cụ thể)
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
            return {"color": "RED", "message": "Lỗi"}
        
        vacancy_rate = (available / capacity) * 100

        if vacancy_rate == 0:
            return {"color": "RED", "message": "Hết"}
        elif vacancy_rate <= 30:
            return {"color": "YELLOW", "message": "Đầy"}
        else:
            return {"color": "GREEN", "message": "Trống"}

    def calculateRouting(self):
        """Tính toán trạng thái của TOÀN BỘ hệ thống mỗi lần Frontend/API gọi tới"""
        status_report = []
        
        # Vì tính toán dựa trên state hiện tại của cây, chúng ta duyệt qua mọi board
        for led in self.connectedLEDs:
            displays = []
            
            for route in getattr(led, 'routes_config', []):
                arrow = route.get("arrow", "STRAIGHT")
                
                # Gọi DFS bắt đầu từ route của board này
                total_capacity, total_available = self._calculate_route_stats(route)
                
                # Quyết định màu đèn
                state = self.evaluate_capacity(total_capacity, total_available)
                displays.append({
                    "arrow": arrow,
                    "color": state["color"],
                    "message": state["message"]
                })
            
            # Cập nhật kết quả cho board
            led.updateDisplays(displays)
            
            # Đóng gói JSON trả về cho Frontend render cái bản đồ 2D
            status_report.append({
                "ledID": led.ledID,
                "location": led.locationNode,
                "x": led.x,
                "y": led.y,
                "status": led.connectionStatus,
                "displays": led.displays
            })
            
        return status_report