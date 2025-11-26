import pandas as pd

class EMA_Crossover:
    """
    Estrategia simple de cruces de medias exponenciales (EMA).
    Genera señales de entrada/salida tipo long (no short).
    """

    def __init__(self, short=20, long=50):
        """
        Parámetros:
        short : int  -> periodo de la EMA corta
        long  : int  -> periodo de la EMA larga
        """
        self.short = short
        self.long = long

    def _ema(self, series: pd.Series, span: int):
        return series.ewm(span=span, adjust=False).mean()

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Devuelve un DataFrame con dos columnas: 'entry' y 'exit'
        Cada una booleana indicando cuándo entrar o salir.
        """
        data = df.copy()

        # Calcular EMAs
        data["ema_short"] = self._ema(data["close"], self.short)
        data["ema_long"] = self._ema(data["close"], self.long)

        # Señales:
        # Entrada: ema_short cruza por encima de ema_long
        data["entry"] = (data["ema_short"] > data["ema_long"]) & \
                        (data["ema_short"].shift() <= data["ema_long"].shift())

        # Salida: ema_short cruza por debajo de ema_long
        data["exit"] = (data["ema_short"] < data["ema_long"]) & \
                       (data["ema_short"].shift() >= data["ema_long"].shift())

        # Mantener solo columnas útiles
        return data[["entry", "exit", "ema_short", "ema_long"]]
