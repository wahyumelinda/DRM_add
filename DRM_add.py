import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, time
import time as tm

# URL dari Google Apps Script Web App (Ganti dengan URL Web App Anda)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz2Vh1CdA0aL1T_YmKgK0zHbayEwCJkV7hJKsc2Ev6stYJueWLBn_0q2fP1YP_NVosc/exec"

# Fungsi untuk mendapatkan semua data dari Google Sheets
def get_all_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, params={"action": "get_data"}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return []

# Ambil data dari Google Sheets
all_data = get_all_data()

# Tampilkan di Streamlit
st.title("Daftar Riwayat Mesin")

if isinstance(all_data, list) and len(all_data) > 0:
    # Konversi data ke DataFrame
    df = pd.DataFrame(all_data, columns=[
        "ID", "BU", "Line", "Produk", "Mesin", "Tanggal", 
        "Mulai", "Selesai", "Masalah", "Tindakan", 
        "Deskripsi", "Quantity", "PIC", "Approval", "Mengetahui"
    ])

    # Menampilkan data sebagai tabel
    st.subheader("Data Keseluruhan")
    st.dataframe(df)

    # Tambahkan visualisasi sederhana (misalnya, jumlah entri per masalah)
    st.subheader("Visualisasi Masalah")
    masalah_counts = df["Masalah"].value_counts().reset_index()
    masalah_counts.columns = ["Masalah", "Jumlah"]
    st.bar_chart(masalah_counts.set_index("Masalah"))
else:
    st.warning("Tidak ada data yang tersedia.")

# Fungsi untuk mendapatkan opsi dari Google Sheets
def get_options():
    try:
        response = requests.get(APPS_SCRIPT_URL, params={"action": "get_options"}, timeout=10)
        response.raise_for_status()
        options = response.json()
        # Tambahkan opsi kosong "" sebagai default di setiap kategori
        for key in options:
            options[key].insert(0, "")
        return options
    except requests.exceptions.RequestException as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return {}

# Fungsi untuk mengirim data ke Google Sheets
def add_data(form_data):
    try:
        response = requests.post(APPS_SCRIPT_URL, json=form_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}

# Ambil data untuk select box
options = get_options()

# Cek dan set default di session_state jika belum ada
defaults = {
    "form_bu": "",
    "form_line": "",
    "form_produk": "",
    "form_mesin": "",
    "form_masalah": "",
    "form_tindakan": "",
    "form_deskripsi": "",
    "form_pic": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "form_add_reset" not in st.session_state:
    st.session_state.form_add_reset = False

if st.session_state.form_add_reset:
    for key, value in defaults.items():
        st.session_state[key] = value
    st.session_state.form_add_reset = False

# Streamlit UI
st.title("Tambah Data ke Google Sheets")

with st.form("add_data_form"):
    st.subheader("Isi Data Berikut:")

    bu = st.selectbox("BU", options.get("BU", [""]), key="form_bu")
    line = st.selectbox("Line", options.get("Line", [""]), key="form_line")
    produk = st.selectbox("Produk", options.get("Produk", [""]), key="form_produk")
    mesin = st.selectbox("Mesin", options.get("Mesin", [""]), key="form_mesin")

    tanggal = st.date_input("Tanggal Pengerjaan")
    mulai = st.time_input("Waktu Mulai")
    selesai = st.time_input("Waktu Selesai")

    masalah = st.selectbox("Masalah", options.get("Masalah", [""]), key="form_masalah")
    tindakan = st.selectbox("Tindakan Perbaikan", options.get("Tindakan Perbaikan", [""]), key="form_tindakan")
    deskripsi = st.selectbox("Deskripsi Sparepart", options.get("Deskripsi", [""]), key="form_deskripsi")
    quantity = st.number_input("Quantity", min_value=0, value=0)
    pic = st.selectbox("PIC", options.get("PIC", [""]), key="form_pic")

    submitted = st.form_submit_button("Tambah Data")

    if submitted:
        if selesai <= mulai:
            st.error("Waktu selesai harus lebih besar dari waktu mulai.")
        else:
            data_to_send = {
                "action": "add_data",
                "BU": bu,
                "Line": line,
                "Produk": produk,
                "Mesin": mesin,
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Mulai": mulai.strftime("%H:%M"),
                "Selesai": selesai.strftime("%H:%M"),
                "Masalah": masalah,
                "Tindakan": tindakan,
                "Deskripsi": deskripsi,
                "Quantity": int(quantity),
                "PIC": pic
            }

            response = add_data(data_to_send)

            if response.get("status") == "success":
                st.toast("Data berhasil ditambahkan!", icon="✅")
                tm.sleep(2)
                st.session_state.form_add_reset = True
                st.rerun()
            else:
                st.error(f"Gagal menambahkan data: {response.get('error', 'Tidak diketahui')}")