
import csv
import matplotlib.pyplot as plt

hasil_trading = []

with open("trades.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        hasil_trading.append(float(row["hasil"]))

if not hasil_trading:
    print("Belum ada transaksi untuk digambar.")
else:
    modal_awal = 1000
    saldo = modal_awal
    equity = [saldo]

    for hasil in hasil_trading:
        saldo += hasil
        equity.append(saldo)

    transaksi = list(range(len(equity)))

    plt.figure(figsize=(10, 5))
    plt.plot(transaksi, equity, marker="o")
    plt.axhline(modal_awal, linestyle="--")

    plt.title("Trading Equity Curve")
    plt.xlabel("Jumlah transaksi")
    plt.ylabel("Saldo akun")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
