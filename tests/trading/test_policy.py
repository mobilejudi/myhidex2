import pytest
from trading.policy import TradePolicy, PolicyState

@pytest.fixture
def default_policy():
    """Returns a default trade policy for testing."""
    return TradePolicy(
        per_trade_limit_sol=10.0,
        daily_notional_limit_sol=100.0,
    )

@pytest.fixture
def policy_state():
    """Returns a fresh policy state for each test."""
    return PolicyState()

def test_can_spend_allowed(default_policy, policy_state):
    """Tests that a trade within limits is allowed."""
    assert policy_state.can_spend(5.0, default_policy) is True

def test_can_spend_exceeds_per_trade_limit(default_policy, policy_state):
    """Tests that a trade exceeding the per-trade limit is blocked."""
    assert policy_state.can_spend(15.0, default_policy) is False

def test_can_spend_exceeds_daily_limit(default_policy, policy_state):
    """Tests that trades are blocked after exceeding the daily limit."""
    policy_state.day_used_sol = 95.0
    assert policy_state.can_spend(10.0, default_policy) is False

def test_can_spend_at_daily_limit(default_policy, policy_state):
    """Tests that a trade is allowed if it exactly meets the daily limit."""
    policy_state.day_used_sol = 90.0
    assert policy_state.can_spend(10.0, default_policy) is True

def test_track_updates_daily_usage(policy_state):
    """Tests that the track method correctly updates the daily SOL usage."""
    assert policy_state.day_used_sol == 0.0
    policy_state.track(25.5)
    assert policy_state.day_used_sol == 25.5
    policy_state.track(10.0)
    assert policy_state.day_used_sol == 35.5
