import asyncio
from converters import *


def main():
    converter = CurrencyConverter()

    try:
        amount = float(input("Введите значение в USD: "))
        print(f"{amount} USD to RUB: {converter.convert('RUB', amount)}")
        print(f"{amount} USD to EUR: {converter.convert('EUR', amount)}")
        print(f"{amount} USD to GBP: {converter.convert('GBP', amount)}")
        print(f"{amount} USD to CNY: {converter.convert('CNY', amount)}")
    except ValueError as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()