
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path
from datetime import date
from io import BytesIO

from openpyxl import load_workbook
from openpyxl.chart import PieChart, LineChart, Reference
from openpyxl.styles import Font, PatternFill
from openpyxl.chart.label import DataLabelList

# KONFIGURASI DASHBOARD
st.set_page_config(
    page_title="Trading Journal Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Trading Journal Analyzer")
st.write("Catat dan analisis performa trading kamu.")

FILE = Path(__file__).parent / "trades.csv"
kolom = ["Tanggal", "Pair", "Hasil"]

# MEMBACA DATA
if FILE.exists():
    try:
        df = pd.read_csv(FILE)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=kolom)
else:
    df = pd.DataFrame(columns=kolom)

for nama_kolom in kolom:
    if nama_kolom not in df.columns:
        df[nama_kolom] = pd.Series(dtype="object")

df = df[kolom].copy()
df["Hasil"] = pd.to_numeric(
    df["Hasil"], errors="coerce"
).fillna(0)

# Simpan seluruh data untuk analisis semua pair
df_semua_pair = df.copy()

# FORM INPUT TRANSAKSI
st.subheader("➕ Tambahkan Transaksi")

with st.form("form_transaksi", clear_on_submit=True):
    tanggal = st.date_input(
        "Tanggal transaksi",
        value=date.today()
    )

    pair = st.selectbox(
        "Pair",
        ["XAUUSD", "EURUSD", "GBPUSD", "YM", "ES", "NQ"]
    )

    hasil = st.number_input(
        "Profit / Loss ($)",
        value=0.0,
        step=1.0,
        help="Profit positif, loss negatif."
    )

    submit = st.form_submit_button("Simpan Transaksi")

    if submit:
        transaksi_baru = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Pair": pair,
            "Hasil": hasil
        }])

        df_simpan = pd.concat(
            [df, transaksi_baru],
            ignore_index=True
        )

        df_simpan.to_csv(FILE, index=False)
        st.success("Transaksi berhasil disimpan!")
        st.rerun()


# PIE CHART FREKUENSI PAIR
st.divider()
st.subheader("🥧 Frekuensi Pair Trading")

if not df_semua_pair.empty:
    frekuensi_pair = (
        df_semua_pair["Pair"]
        .dropna()
        .value_counts()
        .rename_axis("Pair")
        .reset_index(name="Jumlah Trade")
    )

    fig_pair = px.pie(
        frekuensi_pair,
        names="Pair",
        values="Jumlah Trade",
        hole=0.4,
        title="Distribusi Transaksi per Pair"
    )

    fig_pair.update_traces(
        textinfo="label+percent",
        hovertemplate=(
            "Pair: %{label}<br>"
            "Jumlah trade: %{value}<br>"
            "Persentase: %{percent}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig_pair,
        use_container_width=True
    )
else:
    st.info("Belum ada data transaksi untuk ditampilkan.")

# FILTER DAN STATISTIK TRADING
st.divider()
st.subheader("📊 Statistik Trading")

daftar_pair = ["Semua Pair"] + sorted(
    df["Pair"].dropna().unique().tolist()
)

pair_pilihan = st.selectbox(
    "🔎 Filter berdasarkan pair",
    daftar_pair
)

if pair_pilihan == "Semua Pair":
    df = df.copy()
else:
    df = df[df["Pair"] == pair_pilihan].copy()


if df.empty:
    st.info(
        "Belum ada transaksi. Tambahkan transaksi pertamamu di atas."
    )

else:
    jumlah_win = (df["Hasil"] > 0).sum()
    jumlah_loss = (df["Hasil"] < 0).sum()
    total_trades = len(df)

    transaksi_berhasil = jumlah_win + jumlah_loss

    if transaksi_berhasil > 0:
        win_rate = jumlah_win / transaksi_berhasil * 100
    else:
        win_rate = 0.0

    net_profit = df["Hasil"].sum()

    gross_profit = df.loc[
        df["Hasil"] > 0, "Hasil"
    ].sum()

    gross_loss = abs(
        df.loc[df["Hasil"] < 0, "Hasil"].sum()
    )
 
    # Rata-rata profit dan loss
    average_win = (
        df.loc[df["Hasil"] > 0, "Hasil"].mean()
    )

    average_loss = abs(
        df.loc[df["Hasil"] < 0, "Hasil"].mean()
    )

    
    # Perbandingan rata-rata profit dan loss
    if pd.notna(average_win) and pd.notna(average_loss):
        if average_loss > 0:
            win_loss_ratio = average_win / average_loss
        else:
            win_loss_ratio = None
    else:
        win_loss_ratio = None

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    else:
        profit_factor = None

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net Profit", f"${net_profit:.2f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Winning Trades", jumlah_win)
    col5.metric("Losing Trades", jumlah_loss)
    col6.metric(
        "Profit Factor",
        f"{profit_factor:.2f}"
        if profit_factor is not None
        else "N/A"
    )

    col7, col8 = st.columns(2)
    col7.metric("Gross Profit", f"${gross_profit:.2f}")
    col8.metric("Gross Loss", f"${gross_loss:.2f}")
    
    # Advanced Performance Analytics
    st.divider()
    st.subheader("🧠 Advanced Performance Analytics")

    col9, col10 = st.columns(2)

    col9.metric(
        "💰 Average Win",
        f"${average_win:,.2f}"
        if pd.notna(average_win)
        else "$0.00"
    )

    col10.metric(
        "📉 Average Loss",
        f"${average_loss:,.2f}"
        if pd.notna(average_loss)
        else "$0.00"
    )

    st.metric(
        "⚖️ Average Win/Loss Ratio",
        f"{win_loss_ratio:.2f}:1"
        if win_loss_ratio is not None
        else "N/A"
    )

    
    # PIE CHART HASIL TRADING
    st.divider()
    st.subheader("🎯 Distribusi Hasil Trading")

    jumlah_breakeven = (
        (df["Hasil"] == 0).sum()
    )

    hasil_trading = pd.DataFrame({
        "Hasil": ["Win", "Loss", "Breakeven"],
        "Jumlah": [
            int(jumlah_win),
            int(jumlah_loss),
            int(jumlah_breakeven)
        ]
    })

    # Hilangkan kategori dengan jumlah nol
    hasil_trading = hasil_trading[
        hasil_trading["Jumlah"] > 0
    ]

    fig_hasil = px.pie(
        hasil_trading,
        names="Hasil",
        values="Jumlah",
        hole=0.4,
        title="Win vs Loss vs Breakeven"
    )

    fig_hasil.update_traces(
        textinfo="label+percent",
        hovertemplate=(
            "%{label}<br>"
            "Jumlah: %{value}<br>"
            "Persentase: %{percent}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig_hasil,
        use_container_width=True
    )

    # EQUITY CURVE DAN MAXIMUM DRAWDOWN
    st.divider()
    st.subheader("📈 Equity Curve")

    modal_awal = st.number_input(
        "Modal awal ($)",
        min_value=0.0,
        value=1000.0,
        step=100.0
    )

    grafik_df = df.copy()
    grafik_df["Tanggal"] = pd.to_datetime(
        grafik_df["Tanggal"], errors="coerce"
    )

    grafik_df = grafik_df.dropna(
        subset=["Tanggal"]
    ).copy()

    # Urutkan berdasarkan tanggal dan pertahankan
    # urutan asli untuk transaksi pada tanggal yang sama
    grafik_df = grafik_df.sort_values(
        "Tanggal", kind="stable"
    ).reset_index(drop=True)

    if not grafik_df.empty:
        grafik_df["Equity"] = (
            modal_awal + grafik_df["Hasil"].cumsum()
        )
        # Puncak equity memperhitungkan modal awal
        grafik_df["Peak"] = (
        grafik_df["Equity"]
        .cummax()
        .clip(lower=modal_awal)
        )

        # Puncak equity sampai setiap transaksi
        grafik_df["Peak"] = grafik_df["Equity"].cummax()

        # Drawdown dalam dolar
        grafik_df["Drawdown"] = (
            grafik_df["Peak"] - grafik_df["Equity"]
        )

        # Drawdown dalam persentase
        grafik_df["Drawdown %"] = (
            grafik_df["Drawdown"]
            / grafik_df["Peak"].where(
                grafik_df["Peak"] > 0
            )
            * 100
        ).fillna(0)

        max_drawdown = grafik_df["Drawdown"].max()
        max_drawdown_pct = grafik_df["Drawdown %"].max()

        fig_equity = px.line(
            grafik_df,
            x="Tanggal",
            y="Equity",
            markers=True,
            title="Pertumbuhan Equity"
        )

        fig_equity.update_traces(
            line=dict(width=3),
            hovertemplate=(
                "Tanggal: %{x|%d-%m-%Y}<br>"
                "Equity: $%{y:,.2f}"
                "<extra></extra>"
            )
        )

        fig_equity.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Equity ($)",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_equity,
            use_container_width=True
        )

        # METRIK RISIKO
        st.subheader("📉 Risiko Trading")

        col9, col10 = st.columns(2)
        col9.metric(
            "Maximum Drawdown",
            f"${max_drawdown:.2f}"
        )
        col10.metric(
            "Maximum Drawdown (%)",
            f"{max_drawdown_pct:.2f}%"
        )

        # RIWAYAT TRANSAKSI
        st.divider()
        st.subheader("📋 Riwayat Trading")

        tabel_df = df.copy()
        tabel_df.index = range(1, len(tabel_df) + 1)
        tabel_df.index.name = "No"

        st.dataframe(
            tabel_df,
            use_container_width=True
        )

    else:
        st.warning(
            "Belum ada tanggal transaksi yang valid "
            "untuk membuat grafik dan menghitung drawdown."
        )

st.caption(f"Lokasi data: {FILE}")

# EXPORT LAPORAN TRADING
st.divider()
st.subheader("📥 Export Laporan Trading")

# Gunakan semua transaksi, bukan hanya pair yang sedang difilter
laporan_df = df_semua_pair.copy()

laporan_df["Tanggal"] = pd.to_datetime(
    laporan_df["Tanggal"], errors="coerce"
)

laporan_df["Hasil"] = pd.to_numeric(
    laporan_df["Hasil"], errors="coerce"
).fillna(0)

laporan_df = laporan_df.sort_values(
    "Tanggal", kind="stable", na_position="last"
).reset_index(drop=True)

# Modal awal laporan
modal_laporan = (
    float(modal_awal)
    if "modal_awal" in locals()
    else 1000.0
)

# Tambahkan data penting ke setiap transaksi
laporan_df["Status"] = laporan_df["Hasil"].apply(
    lambda x: "Win" if x > 0
    else ("Loss" if x < 0 else "Breakeven")
)

laporan_df["Profit Kumulatif"] = (
    laporan_df["Hasil"].cumsum()
)

laporan_df["Equity"] = (
    modal_laporan + laporan_df["Profit Kumulatif"]
)

laporan_df["Peak Equity"] = (
    laporan_df["Equity"]
    .cummax()
    .clip(lower=modal_laporan)
)

laporan_df["Drawdown ($)"] = (
    laporan_df["Peak Equity"] - laporan_df["Equity"]
)

laporan_df["Drawdown (%)"] = (
    laporan_df["Drawdown ($)"]
    / laporan_df["Peak Equity"].where(
        laporan_df["Peak Equity"] > 0
    )
    * 100
).fillna(0)

# Statistik laporan
jumlah_win_export = int((laporan_df["Hasil"] > 0).sum())
jumlah_loss_export = int((laporan_df["Hasil"] < 0).sum())
jumlah_be_export = int((laporan_df["Hasil"] == 0).sum())

trade_valid = jumlah_win_export + jumlah_loss_export

win_rate_export = (
    jumlah_win_export / trade_valid * 100
    if trade_valid > 0 else 0
)

gross_profit_export = laporan_df.loc[
    laporan_df["Hasil"] > 0, "Hasil"
].sum()

gross_loss_export = abs(
    laporan_df.loc[
        laporan_df["Hasil"] < 0, "Hasil"
    ].sum()
)

profit_factor_export = (
    gross_profit_export / gross_loss_export
    if gross_loss_export > 0 else None
)

net_profit_export = laporan_df["Hasil"].sum()

equity_akhir = modal_laporan + net_profit_export

max_dd_export = (
    laporan_df["Drawdown ($)"].max()
    if not laporan_df.empty else 0
)

max_dd_pct_export = (
    laporan_df["Drawdown (%)"].max()
    if not laporan_df.empty else 0
)

# Siapkan data CSV
csv_df = laporan_df.copy()

csv_df["Tanggal"] = csv_df["Tanggal"].dt.strftime(
    "%Y-%m-%d"
)

csv_data = csv_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download CSV Lengkap",
    data=csv_data,
    file_name="laporan_trading_lengkap.csv",
    mime="text/csv"
)

# Siapkan tabel ringkasan dan analisis pair
ringkasan = pd.DataFrame({
    "Metrik": [
        "Total Trades",
        "Winning Trades",
        "Losing Trades",
        "Breakeven Trades",
        "Win Rate (%)",
        "Net Profit ($)",
        "Gross Profit ($)",
        "Gross Loss ($)",
        "Profit Factor",
        "Modal Awal ($)",
        "Equity Akhir ($)",
        "Maximum Drawdown ($)",
        "Maximum Drawdown (%)"
    ],
    "Nilai": [
        len(laporan_df),
        jumlah_win_export,
        jumlah_loss_export,
        jumlah_be_export,
        round(win_rate_export, 2),
        round(net_profit_export, 2),
        round(gross_profit_export, 2),
        round(gross_loss_export, 2),
        round(profit_factor_export, 2)
        if profit_factor_export is not None else "N/A",
        modal_laporan,
        round(equity_akhir, 2),
        round(max_dd_export, 2),
        round(max_dd_pct_export, 2)
    ]
})

pair_stats = (
    laporan_df.groupby("Pair", dropna=False)
    .agg(
        Jumlah_Trade=("Hasil", "size"),
        Net_Profit=("Hasil", "sum"),
        Win=("Hasil", lambda x: (x > 0).sum()),
        Loss=("Hasil", lambda x: (x < 0).sum())
    )
    .reset_index()
)

pair_stats["Frekuensi (%)"] = (
    pair_stats["Jumlah_Trade"]
    / len(laporan_df) * 100
    if len(laporan_df) > 0 else 0
)

pair_stats["Win Rate (%)"] = (
    pair_stats["Win"]
    / (pair_stats["Win"] + pair_stats["Loss"])
    * 100
).fillna(0)

# Buat file Excel di memori
buffer = BytesIO()

with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    csv_df.to_excel(
        writer, sheet_name="Riwayat Trading", index=False
    )
    ringkasan.to_excel(
        writer, sheet_name="Statistik", index=False,
        startrow=0
    )
    pair_stats.to_excel(
        writer, sheet_name="Statistik", index=False,
        startrow=len(ringkasan) + 3
    )

    # Data untuk grafik equity
    kolom_equity = [
        "Tanggal", "Hasil", "Profit Kumulatif",
        "Equity", "Peak Equity",
        "Drawdown ($)", "Drawdown (%)"
    ]

    csv_df[kolom_equity].to_excel(
        writer, sheet_name="Equity Growth", index=False
    )

# Tambahkan grafik Excel
buffer.seek(0)

from openpyxl import load_workbook

wb = load_workbook(buffer)
ws_stat = wb["Statistik"]
ws_equity = wb["Equity Growth"]

# Grafik pie frekuensi pair
if len(pair_stats) > 0:
    pie_pair = PieChart()
    pie_pair.title = "Frekuensi Pair Trading"
    pie_pair.height = 10
    pie_pair.width = 16

    header_pair = len(ringkasan) + 4
    data_pair = Reference(
        ws_stat,
        min_col=2,
        min_row=header_pair,
        max_row=header_pair + len(pair_stats)
    )
    labels_pair = Reference(
        ws_stat,
        min_col=1,
        min_row=header_pair + 1,
        max_row=header_pair + len(pair_stats)
    )

    
    pie_pair.add_data(data_pair, titles_from_data=True)
    pie_pair.set_categories(labels_pair)

    # Tampilkan nama pair dan persentase
    from openpyxl.chart.label import DataLabelList

    pie_pair.dataLabels = DataLabelList()
    pie_pair.dataLabels.showLegendKey = False
    pie_pair.dataLabels.showPercent = True
    pie_pair.dataLabels.showCategoryName = True
    pie_pair.dataLabels.showLeaderLines = True

    # Tampilkan legenda di sebelah kanan
    pie_pair.legend.position = "r"

    ws_stat.add_chart(pie_pair, "E2")


# Grafik pie Win/Loss/Breakeven
ws_stat["J2"] = "Hasil"
ws_stat["K2"] = "Jumlah"
ws_stat["J3"] = "Win"
ws_stat["K3"] = jumlah_win_export
ws_stat["J4"] = "Loss"
ws_stat["K4"] = jumlah_loss_export
ws_stat["J5"] = "Breakeven"
ws_stat["K5"] = jumlah_be_export

pie_hasil = PieChart()
pie_hasil.title = "Distribusi Hasil Trading"
pie_hasil.height = 10
pie_hasil.width = 16

data_hasil = Reference(
    ws_stat, min_col=11, min_row=2, max_row=5
)
labels_hasil = Reference(
    ws_stat, min_col=10, min_row=3, max_row=5
)


pie_hasil.add_data(data_hasil, titles_from_data=True)
pie_hasil.set_categories(labels_hasil)

# Tampilkan nama hasil dan persentase
pie_hasil.dataLabels = DataLabelList()
pie_hasil.dataLabels.showPercent = True
pie_hasil.dataLabels.showCategoryName = True
pie_hasil.dataLabels.showLeaderLines = True

# Legenda di sebelah kanan
pie_hasil.legend.position = "r"

ws_stat.add_chart(pie_hasil, "E18")


# Grafik equity growth
if len(csv_df) > 0:
    line = LineChart()
    line.title = "Equity Growth"
    line.y_axis.title = "Equity ($)"
    line.x_axis.title = "Transaksi"
    line.height = 9
    line.width = 18

    equity_col = kolom_equity.index("Equity") + 1

    data_equity = Reference(
        ws_equity,
        min_col=equity_col,
        min_row=1,
        max_row=len(csv_df) + 1
    )

    line.add_data(data_equity, titles_from_data=True)

    # Gunakan nomor transaksi agar setiap transaksi
    # terlihat meskipun tanggalnya sama
    from openpyxl.chart import Reference as ChartReference
    from openpyxl.chart.axis import ChartLines

    ws_equity["H1"] = "No. Transaksi"
    for i in range(2, len(csv_df) + 2):
        ws_equity.cell(row=i, column=8, value=i - 1)

    categories = ChartReference(
        ws_equity,
        min_col=8,
        min_row=2,
        max_row=len(csv_df) + 1
    )

    line.set_categories(categories)
    ws_equity.add_chart(line, "J2")

# Rapikan tampilan sheet
for ws in wb.worksheets:
    ws.freeze_panes = "A2"

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            "solid", fgColor="1F4E78"
        )

    for column in ws.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )
        ws.column_dimensions[
            column[0].column_letter
        ].width = min(max_length + 3, 30)

buffer = BytesIO()
wb.save(buffer)
buffer.seek(0)

st.download_button(
    label="📊 Download Excel + Grafik",
    data=buffer.getvalue(),
    file_name="Trading_Report.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    )
)
