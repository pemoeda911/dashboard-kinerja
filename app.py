import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard Kinerja Cabang",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk membersihkan dan mengubah kolom angka
def clean_currency(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        x = x.replace(' ', '').replace(',', '').replace('"', '').strip()
        if x == '-' or x == '':
            return 0.0
        try:
            return float(x)
        except ValueError:
            return 0.0
    return 0.0

# Fungsi untuk memuat data (dengan cache agar cepat)
@st.cache_data
def load_data():
    file_name = "KC2604 - KINERJA CABANG BULAN APRIL 2026 - Sheet1.csv"
    
    # Cek apakah file ada di direktori yang sama
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        # Membersihkan nama kolom dari spasi agar tidak error
        df.columns = df.columns.str.strip()
    else:
        # Jika file tidak ditemukan, buat data dummy berdasarkan struktur CSV Anda 
        # agar dashboard tetap bisa didemonstrasikan
        st.warning(f"File '{file_name}' tidak ditemukan. Menggunakan data simulasi.")
        data = {
            'TAHUN': [2026]*100,
            'BULAN': [4]*100,
            'LOB': np.random.choice(['Konsumtif', 'Produktif', 'Suretyship'], 100),
            'nama_kanwil': np.random.choice(['Kanwil 1 (Medan)', 'Kanwil 2 (Padang)', 'Kanwil 3 (Jakarta)', 'Kanwil 4 (Bandung)'], 100),
            'klasifikasi_produk': np.random.choice(['CAC Non-Program', 'CAC Program', 'CBC'], 100),
            'nama_bank': np.random.choice(['BANK MANDIRI', 'BANK NEGARA INDONESIA', 'BANK RAKYAT INDONESIA', 'BANK TABUNGAN NEGARA'], 100),
            'pokok_pembiayaan': np.random.uniform(10000000, 500000000, 100),
            'nilai_ijp': np.random.uniform(500000, 5000000, 100),
            'ijp_acrual': np.random.uniform(100000, 1000000, 100)
        }
        df = pd.DataFrame(data)
        return df

    # Pembersihan Data Aktual
    kolom_angka = ['pokok_pembiayaan', 'nilai_ijp', 'ijp_acrual']
    for col in kolom_angka:
        if col in df.columns:
            df[col] = df[col].apply(clean_currency)
    
    # Isi nilai kosong (NaN) pada kolom teks dengan 'Tidak Diketahui'
    kolom_teks = ['nama_kanwil', 'LOB', 'klasifikasi_produk', 'nama_bank']
    for col in kolom_teks:
        if col in df.columns:
            df[col] = df[col].fillna('Tidak Diketahui')

    return df

# Muat data
df = load_data()

# ==========================================
# SIDEBAR: FILTERING
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/combo-chart--v1.png", width=80)
st.sidebar.title("🔍 Filter Data")

# Filter Kanwil
kanwil_list = ["Semua"] + list(df['nama_kanwil'].unique())
selected_kanwil = st.sidebar.multiselect("Kantor Wilayah", kanwil_list, default="Semua")

# Filter LOB
lob_list = ["Semua"] + list(df['LOB'].unique())
selected_lob = st.sidebar.multiselect("Line of Business (LOB)", lob_list, default="Semua")

# Filter Bank
bank_list = ["Semua"] + list(df['nama_bank'].unique())
selected_bank = st.sidebar.multiselect("Mitra Bank", bank_list, default="Semua")

# Proses Filtering Data
df_filtered = df.copy()

if "Semua" not in selected_kanwil and len(selected_kanwil) > 0:
    df_filtered = df_filtered[df_filtered['nama_kanwil'].isin(selected_kanwil)]

if "Semua" not in selected_lob and len(selected_lob) > 0:
    df_filtered = df_filtered[df_filtered['LOB'].isin(selected_lob)]

if "Semua" not in selected_bank and len(selected_bank) > 0:
    df_filtered = df_filtered[df_filtered['nama_bank'].isin(selected_bank)]

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.title("📊 Dashboard Kinerja Cabang (April 2026)")
st.markdown("---")

# Format Rupiah
def format_rp(angka):
    if pd.isna(angka):
        return "Rp 0"
    return f"Rp {angka:,.0f}".replace(',', '.')

# 1. KPI Cards
total_pembiayaan = df_filtered['pokok_pembiayaan'].sum()
total_ijp = df_filtered['nilai_ijp'].sum()
total_ijp_akrual = df_filtered['ijp_acrual'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.info("Total Pokok Pembiayaan")
    st.metric(label="", value=format_rp(total_pembiayaan))
with col2:
    st.success("Total Nilai IJP")
    st.metric(label="", value=format_rp(total_ijp))
with col3:
    st.warning("Total IJP Akrual")
    st.metric(label="", value=format_rp(total_ijp_akrual))

st.markdown("---")

# 2. Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Tren Nilai IJP per Kanwil")
    df_kanwil = df_filtered.groupby('nama_kanwil')['nilai_ijp'].sum().reset_index()
    fig_kanwil = px.bar(df_kanwil, x='nama_kanwil', y='nilai_ijp', 
                        labels={'nama_kanwil': 'Kanwil', 'nilai_ijp': 'Total IJP (Rp)'},
                        color='nilai_ijp', color_continuous_scale='Blues')
    st.plotly_chart(fig_kanwil, use_container_width=True)

with col_chart2:
    st.subheader("Komposisi LOB (Line of Business)")
    df_lob = df_filtered.groupby('LOB')['pokok_pembiayaan'].sum().reset_index()
    fig_lob = px.pie(df_lob, names='LOB', values='pokok_pembiayaan', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_lob, use_container_width=True)

st.markdown("---")

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.subheader("Top 5 Mitra Bank (Berdasarkan Pokok Pembiayaan)")
    df_bank = df_filtered.groupby('nama_bank')['pokok_pembiayaan'].sum().reset_index()
    df_bank = df_bank.sort_values(by='pokok_pembiayaan', ascending=False).head(5)
    fig_bank = px.bar(df_bank, y='nama_bank', x='pokok_pembiayaan', orientation='h',
                      labels={'nama_bank': 'Mitra Bank', 'pokok_pembiayaan': 'Pokok Pembiayaan'},
                      color='pokok_pembiayaan', color_continuous_scale='Teal')
    fig_bank.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bank, use_container_width=True)

with col_chart4:
    st.subheader("Distribusi IJP Akrual Berdasarkan Klasifikasi Produk")
    df_produk = df_filtered.groupby('klasifikasi_produk')['ijp_acrual'].sum().reset_index()
    fig_produk = px.bar(df_produk, x='klasifikasi_produk', y='ijp_acrual',
                        labels={'klasifikasi_produk': 'Klasifikasi Produk', 'ijp_acrual': 'IJP Akrual'},
                        color='klasifikasi_produk')
    st.plotly_chart(fig_produk, use_container_width=True)

# 3. Data Tabel Mentah
st.markdown("---")
st.subheader("📋 Rincian Data")

# Memastikan kolom tersedia sebelum ditampilkan
kolom_tabel = ['nama_kanwil', 'LOB', 'nama_bank', 'klasifikasi_produk', 'pokok_pembiayaan', 'nilai_ijp', 'ijp_acrual']
kolom_tersedia = [col for col in kolom_tabel if col in df_filtered.columns]

st.dataframe(
    df_filtered[kolom_tersedia], 
    column_config={
        "pokok_pembiayaan": st.column_config.NumberColumn("Pokok Pembiayaan", format="Rp %.2f"),
        "nilai_ijp": st.column_config.NumberColumn("Nilai IJP", format="Rp %.2f"),
        "ijp_acrual": st.column_config.NumberColumn("IJP Akrual", format="Rp %.2f")
    },
    use_container_width=True,
    height=300
)
