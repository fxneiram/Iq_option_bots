#import streamlit as st
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from dateutil import tz

from exchanges.exchange import Exchange


@dataclass
class TradingBot(ABC):
    exchange: Exchange
    pair: str
    entry_value: float
    stop_gain: float
    stop_loss: float
    loss: float = 0.0
    gain: float = 0.0
    lucro: float = 0.0

    @abstractmethod
    def sinal(self, df):
        pass

    def stop_check(self):
        if self.lucro <= float("-" + str(abs(self.stop_loss))):
            print("Tope de pérdida alcanzado!")
            sys.exit()

        if self.lucro >= float(abs(self.stop_gain)):
            print("Tope de ganancia alcanzado")
            sys.exit()

    def get_profit(self, valor):
        valor = valor if valor > 0 else float("-" + str(abs(self.entry_value)))
        self.lucro += round(valor, 2)

        print(f"WIN:{round(valor, 2)}" if valor > 0 else f"LOSS:{round(valor, 2)}")
        print(f"Lucro Líquido:{round(self.lucro, 2)}")
        self.stop_check()

    def wait_complete(self, order_id):
        while True:

            order_status, valor = self.exchange.api.check_win_digital_v2(order_id)

            if order_status:
                return self.get_profit(valor)

    def run(self):

        print(
            f"Iniciando sesión.\nPar: {self.pair} \nDetener al perder: {self.stop_loss} \nDetener al ganar: {self.stop_gain}"
        )
        print(f"Par: {self.pair}")
        print(f"Detener al perder: {self.stop_loss}")
        print(f"Detener al ganar: {self.stop_gain}")

        while True:

            df = self.exchange.candles_to_df(pair=self.pair)
            print(df["close"])
            last_datetime = timestamp_converter(df["from"].iloc[-1])
            tempo_servidor = timestamp_converter(
                self.exchange.api.get_server_timestamp()
            )

            print(f"Última vela: {last_datetime}, Servidor: {tempo_servidor}")

            valor_entrada = float(int(self.exchange.api.get_balance()) // 100)

            entry_sign = self.sinal(df)
            status, order_id = self.exchange.api.buy_digital_spot(
                self.pair, valor_entrada, entry_sign, 5
            )

            if status:
                print(f"Llegó en: {entry_sign}, Valor:{self.entry_value}")
                self.wait_complete(order_id)
            else:
                print("\nERRO AO REALIZAR ORDEM\n\n")


def timestamp_converter(x):
    hora = datetime.strptime(
        datetime.utcfromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
    )
    return hora.replace(tzinfo=tz.gettz("GMT"))
