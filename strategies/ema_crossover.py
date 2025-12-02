# strategies/ema_crossover.py
import pandas as pd
from backtester.strategy_base import StrategyBase

class Strategy(StrategyBase):
    def name(self):
        return "EMA_20_50"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['entry'] = (df['ema20'] > df['ema50']) & (df['ema20'].shift() <= df['ema50'].shift())
        df['exit'] = (df['ema20'] < df['ema50']) & (df['ema20'].shift() >= df['ema50'].shift())
        return df[['entry','exit']]
