# strategies/ema_crossover.py
from strategies.base import StrategyBase
import pandas as pd

class EMACrossover(StrategyBase):

    def __init__(self, fast=20, slow=50):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)

        out["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        out["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()

        out["entry"] = (
            (out["ema_fast"] > out["ema_slow"])
            & (out["ema_fast"].shift() <= out["ema_slow"].shift())
        )

        out["exit"] = (
            (out["ema_fast"] < out["ema_slow"])
            & (out["ema_fast"].shift() >= out["ema_slow"].shift())
        )

        return out[["entry", "exit"]]

