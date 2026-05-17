from LogManager import LogManager


class BarrierService:
    def openBarrier(self, gateId: str) -> bool:
        LogManager.LogEvent(f"Barrier at {gateId} opened")
        return True

    def closeBarrier(self, gateId: str) -> bool:
        LogManager.LogEvent(f"Barrier at {gateId} closed")
        return True