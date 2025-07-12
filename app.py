import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Optimasi Produksi", layout="wide", initial_sidebar_state="expanded")
st.title("\U0001F4CA Optimasi Produksi Furnitur")
st.subheader("Studi Kasus: UKM Mebel Jati 'Jati Indah'")

st.markdown("""
**Deskripsi Kasus:**

Sebuah usaha mebel memiliki sumber daya terbatas:
- Total waktu kerja: **360 jam/minggu**
- Total stok kayu: **160 unit**

Produksi:
- **Meja**:
  - Keuntungan: Rp750.000
  - Waktu pengerjaan: 6 jam
  - Kebutuhan kayu: 4 unit
- **Kursi**:
  - Keuntungan: Rp300.000
  - Waktu pengerjaan: 2 jam
  - Kebutuhan kayu: 1.5 unit

**Pertanyaan:**
Berapa jumlah **meja dan kursi** yang harus diproduksi agar keuntungan **maksimal**, dengan syarat **kedua jenis produk harus diproduksi (x > 0, y > 0)**?
""")

# --- INPUT PARAMETER MODEL ---
st.markdown("**Masukkan Parameter Produksi:**")

col1, col2, col3 = st.columns(3)
with col1:
    profit_meja = st.number_input("Keuntungan per Meja (Rp)", min_value=0, value=750000, step=50000)
    jam_meja = st.number_input("Jam Kerja per Meja", min_value=1.0, value=6.0, step=0.5)
    kayu_meja = st.number_input("Kayu untuk Meja (unit)", min_value=1.0, value=4.0, step=0.5)

with col2:
    profit_kursi = st.number_input("Keuntungan per Kursi (Rp)", min_value=0, value=300000, step=25000)
    jam_kursi = st.number_input("Jam Kerja per Kursi", min_value=1.0, value=2.0, step=0.5)
    kayu_kursi = st.number_input("Kayu untuk Kursi (unit)", min_value=1.0, value=1.5, step=0.5)

with col3:
    total_jam = st.number_input("Total Jam Kerja Tim (per minggu)", min_value=1, value=360, step=10)
    total_kayu = st.number_input("Total Kayu Jati Tersedia (unit)", min_value=1, value=160, step=10)

# --- TITIK POTONG ---
x_intercept1 = total_jam / jam_meja
x_intercept2 = total_kayu / kayu_meja
y_intercept1 = total_jam / jam_kursi
y_intercept2 = total_kayu / kayu_kursi

A_matrix = np.array([[jam_meja, jam_kursi], [kayu_meja, kayu_kursi]])
b_vector = np.array([total_jam, total_kayu])

try:
    intersect_point = np.linalg.solve(A_matrix, b_vector)
except np.linalg.LinAlgError:
    intersect_point = (0, 0)

# --- CARI SEMUA TITIK LAYAK DENGAN x > 0 dan y > 0 ---
x_vals = np.arange(1, int(min(x_intercept1, x_intercept2)) + 1)
y_vals = np.arange(1, int(min(y_intercept1, y_intercept2)) + 1)

valid_solutions = []
for x in x_vals:
    for y in y_vals:
        jam_total = jam_meja * x + jam_kursi * y
        kayu_total = kayu_meja * x + kayu_kursi * y
        if jam_total <= total_jam and kayu_total <= total_kayu:
            profit = profit_meja * x + profit_kursi * y
            valid_solutions.append({'x': x, 'y': y, 'profit': profit, 'jam': jam_total, 'kayu': kayu_total})

if valid_solutions:
    filtered = [s for s in valid_solutions if s['x'] > 1]
    if filtered:
        best = max(filtered, key=lambda item: item['profit'])
    else:
        best = max(valid_solutions, key=lambda item: item['profit'])
    optimal_point = (best['x'], best['y'])
    optimal_profit = best['profit']
    best_solution = [best]  # hanya tampilkan yang terbaik
else:
    optimal_point = (0, 0)
    optimal_profit = 0
    best_solution = []

# --- OUTPUT HASIL ---
if optimal_point != (0, 0):
    st.success(f"\U0001F4CC Solusi Optimal: {optimal_point[0]} Meja dan {optimal_point[1]} Kursi")
    st.metric("\U0001F4B0 Keuntungan Maksimal", f"Rp {optimal_profit:,.0f}")
else:
    st.error("❌ Tidak ditemukan solusi valid dengan x > 0 dan y > 0.")

# --- VISUALISASI GRAFIK ---
fig, ax = plt.subplots(figsize=(10, 5))
x_vals_plot = np.linspace(0, max(x_intercept1, x_intercept2)*1.1, 400)
y1 = (total_jam - jam_meja * x_vals_plot) / jam_kursi

with np.errstate(divide='ignore', invalid='ignore'):
    y2 = (total_kayu - kayu_meja * x_vals_plot) / kayu_kursi

y_feasible = np.minimum(y1, y2)
ax.fill_between(x_vals_plot, 0, y_feasible, where=(y_feasible >= 0), color='green', alpha=0.2, label='Daerah Layak')
ax.plot(x_vals_plot, y1, label='Batas Jam Kerja')
ax.plot(x_vals_plot, y2, label='Batas Stok Kayu')

if optimal_point != (0, 0):
    ax.plot(optimal_point[0], optimal_point[1], 'ro', markersize=10, label=f'Optimal: {optimal_point[0]}, {optimal_point[1]}')

if intersect_point[0] > 0 and intersect_point[1] > 0:
    ax.plot(intersect_point[0], intersect_point[1], 'go', markersize=8, label='Titik Potong Batas')

ax.set_xlabel('Jumlah Meja (x)')
ax.set_ylabel('Jumlah Kursi (y)')
ax.set_title('Grafik Optimasi Produksi (x > 0 dan y > 0)')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- TABEL TITIK VALID ---
if best_solution:
    st.markdown("### \U0001F4CD Titik Produksi Optimal")
    st.table(best_solution)
else:
    st.info("Tidak ada kombinasi meja dan kursi dengan x > 0 dan y > 0 yang memenuhi batasan.")

with st.expander("\U0001F4D8 Penjelasan Rumus Model: Linear Programming"):
    st.markdown(r"""
Linear Programming adalah metode untuk mencapai hasil terbaik (seperti keuntungan maksimal atau biaya minimal) dalam suatu model matematika yang persyaratannya diwakili oleh hubungan linear.

- **Fungsi Tujuan**: Ini adalah formula yang ingin kita maksimalkan (keuntungan) atau minimalkan (biaya).
- **Fungsi Kendala**: Ini adalah batasan aturan yang harus dipatuhi, seperti sumber daya yang terbatas (jam kerja, bahan baku).

#### Variabel Keputusan:
- $x$ = Jumlah Meja  
- $y$ = Jumlah Kursi

#### Fungsi Tujuan (Maksimalkan Keuntungan):
\[
Z = {:,}\times x + {:,}\times y
\]
""".format(profit_meja, profit_kursi))

    st.markdown(f"""
#### Fungsi Kendala:
1. \( {jam_meja}x + {jam_kursi}y \\le {total_jam} \)
2. \( {kayu_meja}x + {kayu_kursi}y \\le {total_kayu} \)
3. \( x > 0,\ y > 0 \)
""")

with st.expander("\U0001F4CA Lihat Proses Perhitungan"):
    if best_solution:
        x_opt = best['x']
        y_opt = best['y']
        total_jam_terpakai = best['jam']
        total_kayu_terpakai = best['kayu']
        st.latex(f"Z = {profit_meja:,}x + {profit_kursi:,}y")
        st.subheader("Fungsi Kendala dengan Angka:")
        st.latex(f"{jam_meja}x + {jam_kursi}y \\le {total_jam}")
        st.latex(f"{kayu_meja}x + {kayu_kursi}y \\le {total_kayu}")
        st.subheader("Evaluasi Solusi Optimal:")
        st.markdown(f"- Titik: \\( x = {x_opt},\\ y = {y_opt} \\)")
        st.latex(f"{jam_meja} \\times {x_opt} + {jam_kursi} \\times {y_opt} = {total_jam_terpakai} \\le {total_jam}")
        st.latex(f"{kayu_meja} \\times {x_opt} + {kayu_kursi} \\times {y_opt} = {total_kayu_terpakai} \\le {total_kayu}")
        st.markdown(f"**Keuntungan Maksimal: Rp {optimal_profit:,.0f}**")
    else:
        st.info("Belum ditemukan solusi optimal untuk ditampilkan.")