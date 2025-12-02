# backtester/engine.py
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Trade:
    entry_index: int
    entry_time: datetime
    entry_price: float
    exit_index: Optional[int] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    size: float = 0.0
    pnl: Optional[float] = None
    direction: str = "long"  # 'long' or 'short'

class BacktestEngine:
    def __init__(self, df: pd.DataFrame, commission: float = 0.0004, slippage: float = 0.0, fixed_size: float = 1.0):
        """
        df: DataFrame normalizado con columnas datetime, open, high, low, close, volume
        commission: fracción (ej 0.0004 => 0.04%)
        slippage: precio absoluto (ej 1.0 USD) o fracción si prefieres implementarlo así
        fixed_size: tamaño por trade (unidades/contratos)
        """
        self.df = df.reset_index(drop=True)
        self.commission = commission
        self.slippage = slippage
        self.fixed_size = fixed_size
        self.trades = []

    def run(self, signals: pd.DataFrame, entry_price_col='open', exit_price_col='close', allow_short: bool = False):
        """
        signals: DataFrame con 'entry' y 'exit' booleanas (mismo índice que df)
        Simulación simple: entry y exit ejecutados en la misma fila (usamos open para entrar y close para salir)
        """
        position = 0.0
        current_trade: Optional[Trade] = None
        equity = []
        cash = 0.0

        for i, row in self.df.iterrows():
            price_open = float(row[entry_price_col])
            price_close = float(row[exit_price_col])

            # ENTER
            if signals.loc[i, 'entry'] and position == 0:
                exec_price = price_open + self.slippage  # ejecutar con slippage
                # aplicación de comisión en entrada
                entry_price = exec_price * (1 + self.commission)
                position = self.fixed_size
                current_trade = Trade(
                    entry_index=i,
                    entry_time=row['datetime'],
                    entry_price=entry_price,
                    size=position,
                    direction='long'
                )
                self.trades.append(current_trade)

            # EXIT
            elif signals.loc[i, 'exit'] and position != 0:
                exec_price = price_close - self.slippage
                exit_price = exec_price * (1 - self.commission)
                # calcular pnl según dirección
                last = self.trades[-1]
                last.exit_index = i
                last.exit_time = row['datetime']
                last.exit_price = float(exit_price)
                last.pnl = (exit_price - last.entry_price) * last.size
                cash += last.pnl
                position = 0.0
                current_trade = None

            # Equity serie
            equity_val = cash + (position * row['close'])
            equity.append(equity_val)

        eq_series = pd.Series(equity, index=self.df.index)
        trades_df = pd.DataFrame([asdict(t) for t in self.trades])
        return trades_df, eq_series

