import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Optimasi Produksi", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Optimasi Produksi Furnitur")
st.subheader("Studi Kasus: UKM Mebel Jati 'Jati Indah'")

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
x_intercept1 = total_jam / jam_meja if jam_meja > 0 else float('inf')
y_intercept1 = total_jam / jam_kursi if jam_kursi > 0 else float('inf')
x_intercept2 = total_kayu / kayu_meja if kayu_meja > 0 else float('inf')
y_intercept2 = total_kayu / kayu_kursi if kayu_kursi > 0 else float('inf')

A_matrix = np.array([[jam_meja, jam_kursi], [kayu_meja, kayu_kursi]])
b_vector = np.array([total_jam, total_kayu])

try:
    intersect_point = np.linalg.solve(A_matrix, b_vector)
    if intersect_point[0] < 0 or intersect_point[1] < 0:
        intersect_point = (0, 0)
except np.linalg.LinAlgError:
    intersect_point = (0, 0)

corner_points = [(0, 0)]
if y_intercept1 != float('inf') and (kayu_meja*0 + kayu_kursi*y_intercept1 <= total_kayu):
    corner_points.append((0, y_intercept1))
if y_intercept2 != float('inf') and (jam_meja*0 + jam_kursi*y_intercept2 <= total_jam):
    corner_points.append((0, y_intercept2))
if x_intercept1 != float('inf') and (kayu_meja*x_intercept1 + kayu_kursi*0 <= total_kayu):
    corner_points.append((x_intercept1, 0))
if x_intercept2 != float('inf') and (jam_meja*x_intercept2 + jam_kursi*0 <= total_jam):
    corner_points.append((x_intercept2, 0))
if intersect_point[0] > 0 and intersect_point[1] > 0:
    corner_points.append(tuple(intersect_point))

corner_points_unique = sorted(list(set(corner_points)), key=lambda k: (k[0], k[1]))

optimal_profit, optimal_point = 0, (0, 0)
profits_at_corners = []
for x, y in corner_points_unique:
    profit = profit_meja * x + profit_kursi * y
    profits_at_corners.append({'x': round(x, 2), 'y': round(y, 2), 'profit': round(profit, 2)})
    if profit > optimal_profit:
        optimal_profit, optimal_point = profit, (math.floor(x), math.floor(y))

# --- OUTPUT HASIL ---
st.success(f"Produksi optimal adalah {optimal_point[0]} Meja dan {optimal_point[1]} Kursi.")
st.metric("Keuntungan Maksimal", f"Rp {optimal_profit:,.0f}")

# --- VISUALISASI GRAFIK ---
fig, ax = plt.subplots(figsize=(10, 5))
max_x = max(x_intercept1, x_intercept2)
x_vals = np.linspace(0, max_x * 1.1, 400)
y1 = (total_jam - jam_meja * x_vals) / jam_kursi if jam_kursi > 0 else np.full_like(x_vals, float('inf'))
y2 = (total_kayu - kayu_meja * x_vals) / kayu_kursi if kayu_kursi > 0 else np.full_like(x_vals, float('inf'))

y_feasible = np.minimum(y1, y2)
ax.fill_between(x_vals, 0, y_feasible, where=(y_feasible >= 0), color='green', alpha=0.2, label='Daerah Layak')
ax.plot(x_vals, y1, label='Batas Jam Kerja')
ax.plot(x_vals, y2, label='Batas Stok Kayu')
ax.plot(optimal_point[0], optimal_point[1], 'ro', markersize=10, label=f'Optimal: {optimal_point}')

ax.set_xlabel('Jumlah Meja (x)')
ax.set_ylabel('Jumlah Kursi (y)')
ax.set_title('Grafik Optimasi Produksi')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- TABEL TITIK-TITIK SUDUT ---
st.markdown("### 📍 Titik-Titik Sudut dan Keuntungan")
st.table(profits_at_corners)

# --- TABEL TITIK POTONG ---
st.markdown("### 📌 Titik Potong Garis Kendala")
titik_potong = [
    {"Garis": "Jam Kerja (x-intercept)", "x": round(x_intercept1, 2), "y": 0},
    {"Garis": "Jam Kerja (y-intercept)", "x": 0, "y": round(y_intercept1, 2)},
    {"Garis": "Kayu (x-intercept)", "x": round(x_intercept2, 2), "y": 0},
    {"Garis": "Kayu (y-intercept)", "x": 0, "y": round(y_intercept2, 2)},
    {"Garis": "Perpotongan 2 Kendala", "x": round(intersect_point[0], 2), "y": round(intersect_point[1], 2)}
]
st.table(titik_potong)
    