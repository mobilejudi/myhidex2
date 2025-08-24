# trading/policy.py
from dataclasses import dataclass

@dataclass
class TradePolicy:
    max_slippage_bps: int = 200
    max_price_impact_bps: int = 1200
    min_liquidity_usd: float = 20000.0
    block_if_freeze: bool = True
    block_if_mint_auth: bool = True
    daily_notional_limit_sol: float = 200.0
    per_trade_limit_sol: float = 2.0

class PolicyState:
    def __init__(self):
        self.day_used_sol = 0.0
    def can_spend(self, amt_sol: float, p: TradePolicy) -> bool:
        return amt_sol <= p.per_trade_limit_sol and self.day_used_sol + amt_sol <= p.daily_notional_limit_sol
    def track(self, amt_sol: float):
        self.day_used_sol += amt_sol

policy = TradePolicy()
policy_state = PolicyState()
