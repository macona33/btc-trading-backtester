# backtester/metrics.py
import numpy as np
import pandas as pd

def performance_metrics(trades_df: pd.DataFrame, eq_series: pd.Series, periods_per_year: int = 525600) -> dict:
    if eq_series is None or len(eq_series)==0:
        return {}
    total_return = float(eq_series.iloc[-1] - eq_series.iloc[0])
    returns = eq_series.diff().fillna(0)
    mean_period_ret = returns.mean()
    ann_ret = mean_period_ret * periods_per_year
    ann_vol = returns.std() * np.sqrt(periods_per_year)
    sharpe = float(ann_ret / ann_vol) if ann_vol != 0 else float('nan')
    cum = eq_series.cummax()
    drawdown = (eq_series - cum)
    maxdd = float(drawdown.min()) if len(drawdown)>0 else 0.0
    trades = len(trades_df)
    win_rate = float(trades_df[trades_df['pnl']>0].shape[0] / trades) if trades>0 else float('nan')
    expectancy = float(trades_df['pnl'].mean()) if trades>0 else float('nan')
    return {
        'total_return': total_return,
        'annualized_return_est': ann_ret,
        'annualized_vol_est': ann_vol,
        'sharpe_est': sharpe,
        'max_drawdown': maxdd,
        'trades': trades,
        'win_rate': win_rate,
        'expectancy': expectancy
    }

