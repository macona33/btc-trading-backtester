from utils.indicators import ema

class EMACrossover:
    """
    Estrategia simple EMA 20/50.
    El backtester esperará que tenga un método generate_signals(df).
    """

    def __init__(self, fast=20, slow=50):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df):
        df = df.copy()

        df['ema_fast'] = ema(df['close'], self.fast)
        df['ema_slow'] = ema(df['close'], self.slow)

        df['entry'] = (df['ema_fast'] > df['ema_slow']) & \
                      (df['ema_fast'].shift() <= df['ema_slow'].shift())

        df['exit'] = (df['ema_fast'] < df['ema_slow']) & \
                     (df['ema_fast'].shift() >= df['ema_slow'].shift())

        return df[['entry', 'exit']]
