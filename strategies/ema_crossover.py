import pandas as pd

def ema_crossover_strategy(df):
    """
    Estrategia simple EMA 20/50.
    df debe contener columnas: ['open', 'high', 'low', 'close'].
    Devuelve un DataFrame con columnas:
        entry: señal de entrada long
        exit: señal de salida
    """

    df = df.copy()

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    df["entry"] = (df["ema20"] > df["ema50"]) & (df["ema20"].shift() <= df["ema50"].shift())
    df["exit"]  = (df["ema20"] < df["ema50"]) & (df["ema20"].shift() >= df["ema50"].shift())

    return df[["entry","exit"]]
