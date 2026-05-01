import numpy as np
import random
from typing import Tuple, Dict
from config.settings import (
    QL_ALPHA,
    QL_GAMMA,
    QL_EPSILON_START,
    QL_EPSILON_END,
    QL_EPSILON_DECAY,
    QL_REWARD_HIGH_PRIORITY,
    QL_REWARD_AFFECTED,
    QL_REWARD_COMM_GOOD,
    QL_REWARD_EFFICIENT_BATTERY,
    QL_PENALTY_BLOCKED,
    QL_PENALTY_COMM_LOST,
    QL_PENALTY_BATTERY_DRAIN,
    GRID_ROWS,
    GRID_COLS,
)
from environment.cell import CellState

# Actions: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT, 4=STAY
ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
NUM_ACTIONS = len(ACTIONS)


def encode_state(row: int, col: int, battery_bin: int, comm_bin: int) -> int:
    """
    Encode (row, col, battery_bin, comm_bin) into a single integer state index.
    battery_bin: 0=low(<30), 1=med(30-70), 2=high(>70)
    comm_bin:    0=dead(<0.3), 1=weak(0.3-0.7), 2=strong(>0.7)
    """
    return (row * GRID_COLS * 3 * 3) + (col * 3 * 3) + (battery_bin * 3) + comm_bin


STATE_SPACE = GRID_ROWS * GRID_COLS * 3 * 3


class QLearningAgent:
    """
    Tabular Q-Learning agent for a single drone.
    Each drone instance gets its own Q-table, allowing independent learning.
    """

    def __init__(self, drone_id: int):
        self.drone_id = drone_id
        self.q_table = np.zeros((STATE_SPACE, NUM_ACTIONS))
        self.epsilon = QL_EPSILON_START
        self.episode_rewards: list = []
        self.total_reward: float = 0.0
        self.steps: int = 0

    def _battery_bin(self, battery: float) -> int:
        if battery < 30.0:
            return 0
        elif battery < 70.0:
            return 1
        return 2

    def _comm_bin(self, comm: float) -> int:
        if comm < 0.3:
            return 0
        elif comm < 0.7:
            return 1
        return 2

    def get_state(self, row: int, col: int, battery: float, comm: float) -> int:
        return encode_state(row, col, self._battery_bin(battery), self._comm_bin(comm))

    def choose_action(self, state: int) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randint(0, NUM_ACTIONS - 1)
        return int(np.argmax(self.q_table[state]))

    def get_action_delta(self, action_idx: int) -> Tuple[int, int]:
        return ACTIONS[action_idx]

    def compute_reward(
        self, cell, battery: float, prev_battery: float, comm: float
    ) -> float:
        """Compute reward based on cell state and drone status after move."""
        reward = 0.0
        if cell.state == CellState.HIGH_PRIORITY and not cell.visited:
            reward += QL_REWARD_HIGH_PRIORITY
        elif cell.state == CellState.AFFECTED and not cell.visited:
            reward += QL_REWARD_AFFECTED
        if comm >= 0.7:
            reward += QL_REWARD_COMM_GOOD
        elif comm < 0.3:
            reward += QL_PENALTY_COMM_LOST
        battery_drain = prev_battery - battery
        if battery_drain < 3.0:
            reward += QL_REWARD_EFFICIENT_BATTERY
        elif battery_drain > 8.0:
            reward += QL_PENALTY_BATTERY_DRAIN
        if cell.state == CellState.BLOCKED:
            reward += QL_PENALTY_BLOCKED
        return reward

    def update(self, state: int, action: int, reward: float, next_state: int):
        """Q-table update rule: Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') − Q(s,a)]"""
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + QL_ALPHA * (reward + QL_GAMMA * max_next_q - current_q)
        self.q_table[state, action] = new_q
        self.total_reward += reward
        self.steps += 1

    def decay_epsilon(self):
        self.epsilon = max(QL_EPSILON_END, self.epsilon * QL_EPSILON_DECAY)

    def average_reward(self) -> float:
        if self.steps == 0:
            return 0.0
        return self.total_reward / self.steps
