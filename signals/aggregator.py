# signals/aggregator.py
from collections import deque, defaultdict
import time

WINDOWS = {
    "1m": 60_000,
    "5m": 300_000
}

class FeatureState:
    def __init__(self):
        self.events = deque()  # (ts, amount_sol, uniq_smart)
        self.last_price = None
        self.last_price_1m = None
        self.last_price_5m = None

class Aggregator:
    def __init__(self):
        self.by_mint: dict[str, FeatureState] = defaultdict(FeatureState)

    def add(self, mint: str, ts_ms: int, amount_sol: float, uniq_smart: int, price: float | None = None):
        st = self.by_mint[mint]
        st.events.append((ts_ms, amount_sol, uniq_smart))
        # purge
        now = ts_ms
        while st.events and now - st.events[0][0] > WINDOWS["5m"]:
            st.events.popleft()
        if price is not None:
            st.last_price = price

    def features(self, mint: str, now_ms: int):
        st = self.by_mint[mint]
        # calc soma sur 5m
        buys_sol_5m = sum(a for (_, a, _) in st.events)
        uniq_5m = max((u for (_, _, u) in st.events), default=0)
        # momentum fictif (sera remplacé par prix réel)
        ret_1m = 0.0
        ret_5m = 0.0
        return {
            "buys_smart_sol_5m": buys_sol_5m,
            "uniq_smart_5m": uniq_5m,
            "ret_1m": ret_1m,
            "ret_5m": ret_5m
        }

agg = Aggregator()
