from bots.rf_bot import RandomForestBot
from exchanges.iq_option_exchange import IQOptionExchange


def valid_input(message=""):
    while True:
        val = input(message)
        if len(val) > 0:
            return val


def core():
    username = valid_input("Ingrese nombre de usuario: ")
    password = valid_input("Ingrese contraseña: ")

    session_exchange = IQOptionExchange(
        username=username,
        password=password,
        account_type="PRACTICE",
    )

    bot = RandomForestBot(
        exchange=session_exchange,
        entry_value=100,
        stop_gain=10000000000,
        stop_loss=1000,
        pair="EURUSD",
    )
    bot.run()

if __name__ == "__main__":
    core()
