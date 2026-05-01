import pytest
from algorithms.reinforcement.qlearning import (
    QLearningAgent,
    encode_state,
    STATE_SPACE,
    NUM_ACTIONS,
)


def test_state_encoding_in_range():
    from config.settings import GRID_ROWS, GRID_COLS

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            for b in range(3):
                for s in range(3):
                    idx = encode_state(r, c, b, s)
                    assert 0 <= idx < STATE_SPACE


def test_q_table_shape():
    agent = QLearningAgent(0)
    assert agent.q_table.shape == (STATE_SPACE, NUM_ACTIONS)


def test_epsilon_decays():
    agent = QLearningAgent(0)
    initial = agent.epsilon
    for _ in range(100):
        agent.decay_epsilon()
    assert agent.epsilon < initial


def test_q_update_changes_value():
    agent = QLearningAgent(0)
    s, a, r, ns = 0, 0, 100.0, 1
    old_q = agent.q_table[s, a]
    agent.update(s, a, r, ns)
    assert agent.q_table[s, a] != old_q


def test_choose_action_valid():
    agent = QLearningAgent(0)
    action = agent.choose_action(0)
    assert 0 <= action < NUM_ACTIONS
