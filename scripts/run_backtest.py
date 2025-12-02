# scripts/run_backtest.py
import argparse
from pathlib import Path
import pandas as pd
import importlib.util
import sys
from backtester.engine import BacktestEngine
from backtester.metrics import performance_metrics

def load_strategy(path_to_py: str):
    spec = importlib.util.spec_from_file_location("user_strategy", path_to_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # la estrategia debe exponer una clase llamada Strategy que herede StrategyBase
    StrategyClass = getattr(mod, 'Strategy', None)
    if StrategyClass is None:
        raise RuntimeError("El archivo de strategy debe definir una clase 'Strategy'")
    return StrategyClass()

def normalize_parquets(folder: Path) -> pd.DataFrame:
    files = list(folder.glob("*.parquet"))
    if not files:
        raise RuntimeError("No hay .parquet en la carpeta")
    dfs = []
    for f in sorted(files):
        df = pd.read_parquet(f)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True, sort=False)
    # intentamos nombres comunes
    if 'open_time' in df.columns and 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df['open_time'], unit='ms', origin='unix', errors='coerce')
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    for col in ['open','high','low','close','volume']:
        if col not in df.columns:
            # intenta por coincidencias
            for c in df.columns:
                if c.lower()==col:
                    df = df.rename(columns={c:col})
    df = df.dropna(subset=['datetime','close'])
    df = df.sort_values('datetime').reset_index(drop=True)
    return df[['datetime','open','high','low','close','volume']]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('data_folder', help='Carpeta con .parquet')
    p.add_argument('strategy_file', help='Archivo .py con la estrategia (ej strategies/ema_crossover.py)')
    p.add_argument('--output', default='results', help='Carpeta salida')
    return p.parse_args()

def main():
    args = parse_args()
    data_folder = Path(args.data_folder)
    strategy_file = Path(args.strategy_file)
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    print("Cargando datos...")
    df = normalize_parquets(data_folder)
    print(f"Datos cargados: {len(df)} filas desde {df['datetime'].iloc[0]} a {df['datetime'].iloc[-1]}")
    print("Cargando estrategia:", strategy_file)
    strat = load_strategy(str(strategy_file))
    signals = strat.generate_signals(df)
    engine = BacktestEngine(df, commission=0.0004, slippage=0.0, fixed_size=1.0)
    trades, eq = engine.run(signals)
    metrics = performance_metrics(trades, eq)
    print("Métricas:", metrics)
    trades.to_csv(out / f"trades_{strat.name()}.csv", index=False)
    eq.to_csv(out / f"equity_{strat.name()}.csv", index=False)
    import matplotlib.pyplot as plt
    plt.plot(eq.values); plt.title(f"Equity {strat.name()}"); plt.savefig(out / f"equity_{strat.name()}.png")
    print("Resultados guardados en:", out)

if __name__ == '__main__':
    main()

