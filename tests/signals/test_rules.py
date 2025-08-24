import pytest
from signals.rules import Context, strength

def test_strength_strong_signal():
    """Tests the strength function with a strong signal context."""
    ctx = Context(
        token_id=1,
        buys_smart_sol_5m=100.0,
        unique_smart_buyers_5m=5,
        ret_1m=0.15,
        ret_5m=0.30,
        liquidity_usd=50000.0,
        price_impact_1sol_bps=10.0,
        risk_penalties=0.2,
    )
    score, reason = strength(ctx)
    assert 2.0 < score <= 3.0
    assert reason is not None

def test_strength_weak_signal():
    """Tests the strength function with a weak signal context."""
    ctx = Context(
        token_id=2,
        buys_smart_sol_5m=1.0,
        unique_smart_buyers_5m=1,
        ret_1m=-0.05,
        ret_5m=-0.10,
        liquidity_usd=10000.0,
        price_impact_1sol_bps=100.0,
        risk_penalties=2.0,  # Increased penalty to make the signal weaker
    )
    score, reason = strength(ctx)
    assert 0.0 <= score < 1.0

def test_strength_high_risk_signal():
    """Tests the strength function with a high risk context."""
    ctx = Context(
        token_id=3,
        buys_smart_sol_5m=150.0,
        unique_smart_buyers_5m=8,
        ret_1m=0.20,
        ret_5m=0.40,
        liquidity_usd=60000.0,
        price_impact_1sol_bps=5.0,
        risk_penalties=2.5,  # High risk
    )
    score, reason = strength(ctx)
    # The risk score component will be low, dragging down the total score
    assert 0.0 <= score < 2.0

def test_strength_zero_inputs_and_max_risk():
    """Tests the strength function with zero inputs and maximum risk."""
    ctx = Context(
        token_id=4,
        buys_smart_sol_5m=0.0,
        unique_smart_buyers_5m=0,
        ret_1m=0.0,
        ret_5m=0.0,
        liquidity_usd=0.0,
        price_impact_1sol_bps=0.0,
        risk_penalties=3.0,  # Max risk should result in a zero score component
    )
    score, reason = strength(ctx)
    assert score == 0.0

def test_strength_score_bounds():
    """Ensures the score is always within the [0, 3] bounds."""
    # Context designed to push score above 3 before clamping
    ctx_high = Context(
        token_id=5,
        buys_smart_sol_5m=10000.0,
        unique_smart_buyers_5m=20,
        ret_1m=1.0,
        ret_5m=2.0,
        liquidity_usd=1000000.0,
        price_impact_1sol_bps=1.0,
        risk_penalties=0.0,
    )
    score_high, _ = strength(ctx_high)
    assert 0.0 <= score_high <= 3.0

    # Context designed to push score below 0 before clamping (e.g., negative momentum)
    ctx_low = Context(
        token_id=6,
        buys_smart_sol_5m=0,
        unique_smart_buyers_5m=0,
        ret_1m=-1.0,
        ret_5m=-2.0,
        liquidity_usd=0,
        price_impact_1sol_bps=1000.0,
        risk_penalties=3.0,
    )
    score_low, _ = strength(ctx_low)
    assert 0.0 <= score_low <= 3.0
