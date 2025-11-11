import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
from datetime import datetime
from PIL import Image

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="SITOPTENKIT",
    page_icon="💊",
    layout="wide",
)

# --- Gaya CSS ---
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            color: #1E88E5;
            font-size: 32px;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            color: #555;
            font-size: 18px;
        }
        .book-box {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: #f9f9f9;
        }
        .banner {
            background-color: #FFF8E1;
            border-left: 8px solid #FFC107;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 8px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- Path file ---
DATA_PATH = "data/data_penyakit.csv"
ANNOUNCE_PATH = "data/pengumuman.txt"
BANNER_PATH = "data/banner.jpg"

# --- Judul Aplikasi ---
st.markdown(
    '<p class="title"> 📊 Sistem Informasi 10 Kasus Penyakit Terbesar di Desa Lingkar Tambang 🌿</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">Analisis dan Edukasi Kesehatan Masyarakat</p>',
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "📂 Menu Navigasi",
    ["Dashboard Umum", "Dashboard Admin", "Pusat Informasi & Edukasi Kesehatan"],
)

# ===========================================================
# ========== DASHBOARD UMUM =================================
# ===========================================================
if menu == "Dashboard Umum":
    st.header("👩 Dashboard Umum")

    waktu_sekarang = datetime.now()
    tanggal_hari_ini = waktu_sekarang.strftime("%A, %d %B %Y")
    st.markdown(f"🗓️ **Tanggal hari ini:** {tanggal_hari_ini}")

    st.info(
        "Menampilkan data 10 penyakit terbesar dan tren tahunan berdasarkan laporan dari admin."
    )

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        required_cols = ["Tahun", "Bulan", "Penyakit", "Jumlah Kasus"]

        if all(col in df.columns for col in required_cols):
            # --- Penanda waktu update terakhir ---
            last_updated = datetime.fromtimestamp(os.path.getmtime(DATA_PATH))
            st.caption(
                f"📅 **Data terakhir diperbarui:** {last_updated.strftime('%d %B %Y, %H:%M:%S')}"
            )

            # --- 🔍 Filter Tahun & Bulan Bersebelahan ---
            col1, col2 = st.columns(2)
            with col1:
                tahun_terpilih = st.selectbox(
                    "Pilih Tahun", sorted(df["Tahun"].unique(), reverse=True)
                )
            with col2:
                bulan_terpilih = st.selectbox(
                    "Pilih Bulan", sorted(df["Bulan"].unique())
                )

            data_terpilih = df[
                (df["Tahun"] == tahun_terpilih) & (df["Bulan"] == bulan_terpilih)
            ]

            if data_terpilih.empty:
                st.warning("Tidak ada data untuk periode ini.")
            else:
                top10 = (
                    data_terpilih.groupby("Penyakit")["Jumlah Kasus"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Jumlah Kasus", ascending=False)
                    .head(10)
                )

                st.markdown(
                    f"### 📋 10 Penyakit Terbesar - {bulan_terpilih} {tahun_terpilih}"
                )
                st.dataframe(top10, use_container_width=True)

                # Grafik batang
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(top10["Penyakit"], top10["Jumlah Kasus"], color="#1E88E5")
                plt.xticks(rotation=45, ha="right")
                plt.ylabel("Jumlah Kasus")
                plt.title(f"Top 10 Penyakit - {bulan_terpilih} {tahun_terpilih}")
                st.pyplot(fig)

                # Tren tahunan
                st.markdown("### 📈 Tren Kasus per Penyakit Sepanjang Tahun")
                data_tahun = df[df["Tahun"] == tahun_terpilih]
                tren_tahunan = (
                    data_tahun.groupby(["Bulan", "Penyakit"])["Jumlah Kasus"]
                    .sum()
                    .reset_index()
                )
                penyakit_utama = top10["Penyakit"].tolist()

                fig, ax = plt.subplots(figsize=(10, 5))
                for p in penyakit_utama:
                    subset = tren_tahunan[tren_tahunan["Penyakit"] == p]
                    ax.plot(
                        subset["Bulan"], subset["Jumlah Kasus"], marker="o", label=p
                    )
                plt.xticks(rotation=45)
                plt.title(f"Tren Kasus Penyakit Sepanjang Tahun {tahun_terpilih}")
                plt.legend()
                st.pyplot(fig)

                # Ringkasan tahunan
                st.markdown("### 🧾 Ringkasan Total Kasus per Penyakit (Tahunan)")
                ringkasan_tahunan = (
                    df[df["Tahun"] == tahun_terpilih]
                    .groupby("Penyakit")["Jumlah Kasus"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Jumlah Kasus", ascending=False)
                )
                st.dataframe(ringkasan_tahunan, use_container_width=True)
        else:
            st.error(f"File CSV harus memiliki kolom: {', '.join(required_cols)}")
    else:
        st.warning(
            "Belum ada data yang diunggah oleh admin. Silakan unggah melalui Dashboard Admin."
        )

# ===========================================================
# ========== DASHBOARD ADMIN ================================
# ===========================================================
elif menu == "Dashboard Admin":
    st.header("👩🏻‍⚕️ Dashboard Admin")
    st.warning("Halaman ini hanya untuk pengelola data.")

    # --- Upload Banner Gambar ---
    st.subheader("🖼️ Unggah Banner Gambar")
    uploaded_banner = st.file_uploader(
        "Pilih file banner (JPG/PNG)", type=["jpg", "jpeg", "png"]
    )
    if uploaded_banner:
        os.makedirs("data", exist_ok=True)
        image = Image.open(uploaded_banner)
        image.save(BANNER_PATH)
        st.success(
            "✅ Banner berhasil diperbarui! Coba buka Dashboard Umum untuk melihat hasilnya."
        )
        st.image(BANNER_PATH, caption="Banner Baru", use_container_width=True)

    st.markdown("---")

    # --- 📢 Fitur Pengumuman ---
    st.subheader("📢 Atur Pengumuman Desa")
    os.makedirs("data", exist_ok=True)

    current_announcement = ""
    if os.path.exists(ANNOUNCE_PATH):
        with open(ANNOUNCE_PATH, "r", encoding="utf-8") as f:
            current_announcement = f.read()

    new_announcement = st.text_area(
        "Tulis pengumuman (misal: Posyandu minggu depan di Balai Desa!)",
        value=current_announcement,
        height=100,
    )
    if st.button("💾 Simpan Pengumuman"):
        with open(ANNOUNCE_PATH, "w", encoding="utf-8") as f:
            f.write(new_announcement.strip())
        st.success("📢 Pengumuman berhasil disimpan! Akan tampil di Dashboard Umum.")

    st.markdown("---")

    # --- Upload Data Penyakit ---
    st.subheader("📊 Unggah Data Penyakit")
    uploaded_file = st.file_uploader("📂 Unggah file data penyakit (CSV)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        required_cols = ["Tahun", "Bulan", "Penyakit", "Jumlah Kasus"]

        if all(col in df.columns for col in required_cols):
            st.success("✅ Data berhasil dimuat.")
            st.dataframe(df, use_container_width=True)

            os.makedirs("data", exist_ok=True)
            df.to_csv(DATA_PATH, index=False)
            st.success(
                "💾 Data berhasil disimpan! Dashboard Umum akan menampilkan data terbaru secara otomatis."
            )

            # Tombol unduh ulang
            buffer = BytesIO()
            df.to_excel(buffer, index=False, sheet_name="Data_Penyakit")
            buffer.seek(0)
            st.download_button(
                label="📥 Unduh Salinan Data (Excel)",
                data=buffer,
                file_name="Data_Penyakit_Terbaru.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(f"File CSV harus memiliki kolom: {', '.join(required_cols)}")
    else:
        st.info(
            "Unggah data CSV untuk memperbarui data yang digunakan oleh dashboard umum."
        )

# ===========================================================
# ========== Pusat Informasi & Edukasi KesehataN ===============================
# ===========================================================
elif menu == "Pusat Informasi & Edukasi Kesehatan":
    st.header("📚 Pusat Informasi & Edukasi Kesehatan")

    # --- Banner Gambar (tampil di atas judul) ---
    if os.path.exists(BANNER_PATH):
        st.image(BANNER_PATH, use_container_width=True)
    else:
        st.markdown(
            "<div style='text-align:center;color:gray;'>📸 (Belum ada banner, unggah dari Dashboard Admin)</div>",
            unsafe_allow_html=True,
        )

    # --- 📢 Tampilkan Pengumuman di Halaman Bacaan ---
    if os.path.exists(ANNOUNCE_PATH):
        with open(ANNOUNCE_PATH, "r", encoding="utf-8") as f:
            pengumuman = f.read().strip()
        if pengumuman:
            st.markdown(
                f"<div class='banner'>📢 <b>Pengumuman:</b> {pengumuman}</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        "Berikut beberapa sumber bacaan kesehatan yang bisa diakses secara online:"
    )

    daftar_buku = [
        {
            "judul": "Buku Saku: Masyarakat Sehat Lingkar Tambang",
            "deskripsi": "Panduan ringkas untuk masyarakat sekitar tambang agar hidup sehat dan menjaga lingkungan.",
            "link": "https://www.canva.com/design/DAGs00R5cRU/hQGZLlyvVXjpyCOw18do1Q/edit?utm_content=DAGs00R5cRU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton",
        },
        {
            "judul": "Pedoman Pencegahan dan Pengendalian ISPA",
            "deskripsi": "Panduan dari Kementerian Kesehatan mengenai tata laksana ISPA.",
            "link": "https://pusdatin.kemkes.go.id/resources/download/pusdatin/profil-kesehatan-indonesia/Profil-Kesehatan-Indonesia-2022.pdf",
        },
        {
            "judul": "Pedoman Pengendalian Hipertensi",
            "deskripsi": "Edukasi dan panduan pengendalian tekanan darah tinggi.",
            "link": "https://perki.or.id/wp-content/uploads/2021/12/Pedoman-Hipertensi-PERKI-2021.pdf",
        },
    ]

    for buku in daftar_buku:
        st.markdown(
            f"""
        <div class="book-box">
            <h4>📖 {buku['judul']}</h4>
            <p>{buku['deskripsi']}</p>
            <a href="{buku['link']}" target="_blank">
                <button style="background-color:#1E88E5;color:white;padding:8px 15px;border:none;border-radius:8px;">
                    🔗 Buka Buku
                </button>
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption("📊 Sumber data: Balai Desa Lingkar Tambang | Dibuat oleh PUTRi")
