# # LANGKAH 0 · Menyiapkan alat (import) dan alamat berkas
# # "import" = meminjam kotak perkakas yang sudah dibuat orang lain.
# # pandas : perkakas utama mengolah tabel (seperti Excel versi kode)
# # sqlalchemy + psycopg2 : jembatan Python ke PostgreSQL
# # Path : menulis alamat folder/berkas yang aman di Windows & Mac
# # datetime: mengolah tanggal
# # getpass : meminta password tanpa menampilkannya di layar
# from datetime import datetime
# from getpass import getpass
# from pathlib import Path
# import pandas as pd
# from sqlalchemy import URL, Date, create_engine, text
# # Alamat dihitung dari lokasi skrip ini, sehingga skrip tetap jalan
# # walaupun dijalankan dengan tombol Run () di VS Code.
# # __file__ = berkas skrip ini; .parent = folder di atasnya.
# FOLDER_REPO = Path(__file__).resolve().parent.parent
# BERKAS_MENTAH = FOLDER_REPO / "data" / "daftar_arsip_fakultas.csv"
# FOLDER_OUTPUT = FOLDER_REPO / "output"
# FOLDER_OUTPUT.mkdir(exist_ok=True) # buat folder bila belum ada
# # Tanggal acuan penilaian retensi: akhir tahun 2026, saat unit arsip
# # biasanya menyusun daftar usul musnah. Dibuat tetap (bukan "hari
# # ini") agar hasil semua mahasiswa sama dan bisa dicocokkan.
# TANGGAL_ACUAN = pd.Timestamp("2026-12-31")
# # LANGKAH 1 · Membaca CSV dan mengenali isinya
# # dtype=str : baca semua kolom sebagai teks dulu, supaya tidak ada
# # nilai yang "diubah diam-diam" oleh pandas.
# # keep_default_na=False : sel kosong dibaca sebagai "" (teks kosong).
# df = pd.read_csv(BERKAS_MENTAH, dtype=str, keep_default_na=False)
# print("=== LANGKAH 1 · Kenali data ===")
# print("Jumlah baris, kolom :", df.shape) # (baris, kolom)
# print("Nama kolom :", list(df.columns))
# print(df.head()) # 5 baris pertama
# # LANGKAH 2 · Merapikan teks: buang spasi berlebih
# # Spasi di awal/akhir tidak terlihat, tetapi membuat "Akademik" dan
# # " Akademik" dianggap dua nilai berbeda oleh komputer.
# # for ... in ... : ulangi perintah yang sama untuk setiap kolom.
# for kolom in df.columns:
# df[kolom] = df[kolom].str.strip() # strip = buang spasi tepi
# # Ganti spasi ganda di tengah judul menjadi satu spasi.
# df["judul"] = df["judul"].str.replace(r"\s+", " ", regex=True)
# # LANGKAH 3 · Kosakata terkendali (ingat Sesi 11: metadata konsisten)
# # Kamus (dictionary) Python: { "nilai di data" : "nilai baku" }.
# # Kunci ditulis huruf kecil karena data akan kita kecilkan dulu.
# KAMUS_UNIT = {
# "kepegawaian": "Kepegawaian", "kpg": "Kepegawaian",
# "kepeg.": "Kepegawaian",
# "keuangan": "Keuangan", "keu": "Keuangan", "keu.": "Keuangan",
# "akademik": "Akademik", "akd": "Akademik", "akad.": "Akademik",
# "kemahasiswaan": "Kemahasiswaan", "kmh": "Kemahasiswaan",
# "umum dan perlengkapan": "Umum dan Perlengkapan",
# "umum & perlengkapan": "Umum dan Perlengkapan",
# "ump": "Umum dan Perlengkapan",
# }
# KAMUS_MEDIA = {
# "kertas": "Kertas", "fisik": "Kertas",
# "elektronik": "Elektronik", "digital": "Elektronik",
# "e-arsip": "Elektronik",
# }
# KAMUS_AKSES = {"biasa": "Biasa", "terbatas": "Terbatas",
# "rahasia": "Rahasia"}
# # .str.lower() = jadikan huruf kecil; .map(kamus) = terjemahkan.
# # Nilai yang tidak ada di kamus akan menjadi kosong (NaN): itu
# # tanda ada variasi baru yang harus ditambahkan ke kamus.
# df["unit_pencipta"] = df["unit_pencipta"].str.lower().map(KAMUS_UNIT)
# df["media"] = df["media"].str.lower().map(KAMUS_MEDIA)
# df["tingkat_akses"] = df["tingkat_akses"].str.lower().map(KAMUS_AKSES)
# print("\n=== LANGKAH 3 · Nilai unit setelah dibakukan ===")
# print(df["unit_pencipta"].value_counts(dropna=False))
# # LANGKAH 4 · Menyeragamkan tanggal ke ISO 8601 (YYYY-MM-DD)
# # Data berisi tiga format: 2019-03-14, 14/03/2019, dan 14-03-2019.
# # def = membuat fungsi sendiri. Fungsi ini mencoba tiap format satu
# # per satu; format pertama yang cocok dipakai.
# def baca_tanggal(teks):
# for pola in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
# try:
# return pd.Timestamp(datetime.strptime(teks, pola))
# except ValueError:
# pass # tidak cocok, coba pola lain
# return pd.NaT # NaT = "Not a Time" (kosong)
# # .apply(fungsi) = jalankan fungsi untuk setiap baris kolom itu.
# df["tanggal_arsip"] = df["tanggal_arsip"].apply(baca_tanggal)
# # Kolom bantu "tahun" untuk grafik. Int64 = bilangan bulat yang
# # boleh kosong (agar tidak tampil sebagai 2018.0).
# df["tahun"] = df["tanggal_arsip"].dt.year.astype("Int64")
# # Kolom jumlah_lembar diubah dari teks ke angka (kosong -> NaN).
# df["jumlah_lembar"] = pd.to_numeric(df["jumlah_lembar"],
# errors="coerce").astype("Int64")
# # LANGKAH 5 · Membuang baris duplikat (ekspor ganda)
# jumlah_awal = len(df)
# df = df.drop_duplicates() # hapus baris kembar persis
# print("\n=== LANGKAH 5 · Duplikat ===")
# print("Duplikat dibuang :", jumlah_awal -len(df))
# print("Sisa baris :", len(df))