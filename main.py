import csv
import os

FILE_CSV = "trades.csv"


def muat_transaksi():
    transaksi = []

    if os.path.exists(FILE_CSV):
        with open(FILE_CSV, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                transaksi.append(float(row["hasil"]))

    return transaksi


def simpan_transaksi(hasil):
    file_baru = not os.path.exists(FILE_CSV)

    with open(FILE_CSV, "a", newline="") as file:
        writer = csv.writer(file)

        if file_baru:
            writer.writerow(["hasil"])

        writer.writerow([hasil])


hasil_trading = muat_transaksi()

print("=== TRADING JOURNAL ANALYZER ===")
print("Transaksi tersimpan:", len(hasil_trading))
print("Ketik angka untuk menambahkan transaksi.")
print("Ketik 'selesai' untuk membuat laporan.\n")

while True:
    teks = input("Hasil transaksi: ").strip()

    if teks.lower() == "selesai":
        break

    try:
        hasil = float(teks)
        hasil_trading.append(hasil)
        simpan_transaksi(hasil)
        print("Data berhasil disimpan!\n")
    except ValueError:
        print("Masukkan angka yang valid.\n")


if hasil_trading:
    total = len(hasil_trading)
    wins = [x for x in hasil_trading if x > 0]
    losses = [x for x in hasil_trading if x < 0]

    gross_profit = sum(wins)
    gross_loss = sum(losses)
    net_profit = sum(hasil_trading)

    win_rate = len(wins) / total * 100

    profit_factor = (
        gross_profit / abs(gross_loss)
        if gross_loss != 0 else None
    )

    rata_win = sum(wins) / len(wins) if wins else 0
    rata_loss = sum(losses) / len(losses) if losses else 0

    print("\n=== LAPORAN PERFORMA ===")
    print("Total transaksi:", total)
    print("Win:", len(wins))
    print("Loss:", len(losses))
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Gross profit: {gross_profit:.2f}")
    print(f"Gross loss: {gross_loss:.2f}")
    print(f"Net profit: {net_profit:.2f}")
    print(f"Rata-rata win: {rata_win:.2f}")
    print(f"Rata-rata loss: {rata_loss:.2f}")

    if profit_factor is not None:
        print(f"Profit factor: {profit_factor:.2f}")
    else:
        print("Profit factor: tidak terdefinisi (belum ada loss)")

    print("\nData tersimpan di:", FILE_CSV)
else:
    print("Belum ada data transaksi.")
