# 📚 Dokumentasi Proyek AI Sederhana: Prediksi Stok Kain
Tampilannya bisa dilihat di link ini [Prediksi Stock Kain](https://prediksi-stok-kain.onrender.com/)

## 1. Panduan Pembuatan (Untuk Pengembang) 🛠️
Dokumen ini menjelaskan komponen kode dan langkah-langlangkah yang diperlukan untuk menjalankan dan memelihara aplikasi web Prediksi Stok.
## 1.1. ⚙️ Persyaratan Sistem
Pastikan sistem Anda telah menginstal komponen berikut:
*	Python: Versi 3.6 ke atas.
*	Pip: Package installer Python (biasanya sudah terinstal bersama Python).
## 1.2. 📦 Instalasi Dependensi
Aplikasi ini bergantung pada beberapa library Python utama. Instal semuanya menggunakan pip:
```ruby
Bash
pip install flask pandas xlsxwriter
```

## 1.3. 📂 Struktur Proyek
Aplikasi harus diatur dalam struktur direktori berikut:
```
/nama_proyek
  |-- app.py             # Logika utama (Flask, Prediksi, Upload, Download)
  |-- /templates         # Menyimpan file HTML
        |-- index.html   # Antarmuka web utama
  |-- /uploads           # Dibuat otomatis, tempat menyimpan file CSV sementara
```

## 1.4. 📝 Logika Kode Kunci (app.py)
Aplikasi ini berjalan menggunakan framework Flask, menyimpan data penjualan historis di memori (sebagai variabel global) setelah diunggah.
### A. Data Loading
- Fungsi load_data_from_file(filepath) menggunakan Pandas (pd.read_csv) untuk membaca data.
- Asumsi data: Kolom pertama diabaikan (dianggap sebagai identifier seperti tanggal/bulan), dan kolom-kolom berikutnya adalah jenis-jenis kain (dengan data penjualan numerik).
### B. Model Prediksi
- Fungsi prediksi_stok_sederhana() adalah inti "AI" sederhana ini.
- Perhitungan Utama:
- Rata-Rata Jual: $R = \text{Penjualan Harian/Bulanan Rata-Rata}$.
- Safety Stock (Stok Aman): $SS = R \times \text{Safety Stock Factor}$.
- Reorder Point (Titik Pemesanan Ulang): $RP = R \times \text{Reorder Point Factor}$.
- Rekomendasi:
- Jika $\text{Stok Saat Ini} \le SS$, maka Stok Kritis!
- Jika $SS < \text{Stok Saat Ini} \le RP$, maka Waktunya Pesan Ulang.
- Jika $\text{Stok Saat Ini} > RP$, maka Stok Aman.
### C. Rute Aplikasi
| Rute | Metode	| Tujuan  |
|------|--------|---------|
|  /   | GET/POST	| Menampilkan antarmuka, menangani unggahan file CSV, dan menerima input stok/faktor untuk menjalankan prediksi.|
|/download |	GET	| Mengirimkan hasil prediksi terakhir yang tersimpan di memori sebagai file Excel (.xlsx) menggunakan send_file dari Flask dan xlsxwriter.|
		
## 1.5. 🏃 Cara Menjalankan Aplikasi
Jalankan file app.py dari terminal:
Bash
python app.py
Akses aplikasi melalui browser di alamat yang ditampilkan, biasanya http://127.0.0.1:5000/
________________________________________
# 2. Panduan Penggunaan (Untuk Pengguna Toko Kain) 🛍️
Panduan ini menjelaskan cara menggunakan aplikasi web Prediksi Stok untuk mendapatkan rekomendasi pemesanan ulang kain.
## 2.1. 📍 Akses Aplikasi
Aplikasi Prediksi Stok dapat diakses melalui web browser Anda (Chrome, Firefox, dll.) di alamat: http://127.0.0.1:5000/ (atau alamat yang disediakan oleh IT Anda).
## 2.2. Langkah 1: Unggah Data Penjualan Historis
Data historis adalah "otak" dari sistem prediksi. Ini harus diunggah terlebih dahulu.
1.	Siapkan File CSV: Data harus berupa file CSV (Comma Separated Values).
o	Kolom pertama adalah periode waktu (Bulan, Minggu, atau Tanggal).
o	Kolom-kolom berikutnya adalah Penjualan (dalam meter) untuk setiap jenis kain.
2.	Unggah: Di bagian "Unggah Data Historis (CSV)", klik "Pilih File" dan pilih file CSV Anda.
3.	Klik tombol "Unggah & Muat Data Baru". Halaman akan refresh, dan aplikasi akan menggunakan data kain dari file Anda.
Tips CSV: Jika Anda menggunakan data bulanan dari Januari hingga Desember, file CSV Anda akan memiliki 12 baris data dan satu kolom untuk setiap jenis kain.
## 2.3. Langkah 2: Input Prediksi Stok
Setelah data dimuat, Anda dapat menjalankan prediksi.
### A. Sesuaikan Faktor Perhitungan
Dua faktor ini menentukan seberapa konservatif rekomendasi Anda:
| Faktor | Penjelasan | Pengaruh | Rentang Umum |
|--------|------------|----------|--------------|
|**Safety Stock Factor**|Mengontrol tingkat stok aman (buffer) Anda.|	Nilai lebih Tinggi (misal, 0.8) menghasilkan Stok Aman yang lebih besar.|	0.5 - 1.0 |
|**Reorder Point Factor**|Mengontrol kapan Anda mulai memesan ulang.|	Nilai lebih Tinggi (misal, 2.0) membuat Anda memesan lebih cepat (saat stok masih banyak).|	1.2 - 2.5 |
### B. Masukkan Stok Saat Ini
Masukkan jumlah Stok Kain aktual yang ada di toko Anda saat ini (dalam meter) di setiap kotak input yang tersedia.
### C. Hitung Rekomendasi
Setelah semua data dimasukkan, klik tombol "Hitung Prediksi & Rekomendasi".
## 2.4. Langkah 3: Interpretasi Hasil
Tabel hasil akan muncul di bagian bawah halaman. Perhatikan kolom Rekomendasi dan pewarnaan baris:

|Warna Baris |	Rekomendasi |	Tindakan |
| ---------- | ------------ | ---------- |
|🔴 Merah Muda (Kritis)|	PERLU SEGERA PESAN ULANG (Stok Kritis!)|	Stok Anda telah jatuh di bawah Tingkat Stok Aman. Lakukan pemesanan segera! |
|🟡 Kuning (Perlu)	|Waktunya Pesan Ulang	| Stok Anda berada di antara Titik Pemesanan Ulang dan Stok Aman. Pesan ulang disarankan untuk menghindari kehabisan stok.
|🟢 Hijau (Aman)|	Stok Aman|	Stok Anda berada di atas Titik Pemesanan Ulang. Belum perlu memesan.|


## 2.5. 💾 Download Hasil (Ekspor ke Excel)
Untuk menyimpan atau membagikan hasil prediksi:
1.	Klik tombol "Download Excel" yang terletak di sebelah judul hasil.
2.	File bernama Prediksi_Stok_Kain.xlsx akan diunduh ke komputer Anda.


