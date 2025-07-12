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
- Total waktu kerja: **240 jam/minggu**
- Total stok kayu: **120 unit**

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
    total_jam = st.number_input("Total Jam Kerja Tim (per minggu)", min_value=1, value=240, step=10)
    total_kayu = st.number_input("Total Kayu Jati Tersedia (unit)", min_value=1, value=120, step=10)

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
        if x > 0 and y > 0:
            if jam_meja * x + jam_kursi * y <= total_jam and kayu_meja * x + kayu_kursi * y <= total_kayu:
                profit = profit_meja * x + profit_kursi * y
                valid_solutions.append({'x': x, 'y': y, 'profit': profit})

if valid_solutions:
    best = max(valid_solutions, key=lambda item: item['profit'])
    optimal_point = (best['x'], best['y'])
    optimal_profit = best['profit']
else:
    optimal_point = (0, 0)
    optimal_profit = 0

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
    ax.plot(optimal_point[0], optimal_point[1], 'ro', markersize=10, label=f'Optimal: {optimal_point}')

if intersect_point[0] > 0 and intersect_point[1] > 0:
    ax.plot(intersect_point[0], intersect_point[1], 'go', markersize=8, label='Titik Potong Batas')

ax.set_xlabel('Jumlah Meja (x)')
ax.set_ylabel('Jumlah Kursi (y)')
ax.set_title('Grafik Optimasi Produksi (x > 0 dan y > 0)')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- TABEL TITIK VALID ---
if valid_solutions:
    st.markdown("### \U0001F4CD Titik Produksi Layak dan Keuntungan")
    st.table(valid_solutions)
else:
    st.info("Tidak ada kombinasi meja dan kursi dengan x > 0 dan y > 0 yang memenuhi batasan.")

st.markdown("""
### ℹ️ Penjelasan:
Hanya titik-titik dengan **x > 0 dan y > 0** yang diperiksa agar usaha memproduksi **meja dan kursi secara bersamaan**. Dari semua solusi yang valid terhadap batasan waktu dan kayu, dipilih kombinasi dengan keuntungan maksimal.
""")