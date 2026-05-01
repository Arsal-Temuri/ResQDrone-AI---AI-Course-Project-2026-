from config.settings import (
    BATTERY_DRAIN_PER_MOVE,
    BATTERY_DRAIN_COMM_RELAY,
    BATTERY_RECHARGE_RATE,
    BATTERY_MAX,
)
from drones.drone import Drone, DroneStatus


class BatteryManager:

    @staticmethod
    def drain_move(drone: Drone, cell_risk: float = 0.0):
        """Drain battery on movement. Higher risk cells drain more."""
        drain = BATTERY_DRAIN_PER_MOVE * (1.0 + cell_risk * 0.5)
        drone.battery = max(0.0, drone.battery - drain)

    @staticmethod
    def drain_relay(drone: Drone):
        drone.battery = max(0.0, drone.battery - BATTERY_DRAIN_COMM_RELAY)

    @staticmethod
    def recharge(drone: Drone):
        """Recharge at base station."""
        if drone.battery < BATTERY_MAX:
            drone.battery = min(BATTERY_MAX, drone.battery + BATTERY_RECHARGE_RATE)
        if drone.battery >= BATTERY_MAX:
            drone.battery = BATTERY_MAX
            drone.status = DroneStatus.IDLE
