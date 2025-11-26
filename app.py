import pandas as pd
from typing import Dict, List
from flask import Flask, render_template, request, redirect, url_for, send_file
import os, io

# Konfigurasi aplikasi Flask
app = Flask(__name__)
# Tentukan folder tempat file yang diunggah akan disimpan sementara
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Tentukan jenis file yang diizinkan
ALLOWED_EXTENSIONS = {'csv'}

# --- Fungsi Utility ---
def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan (hanya CSV)."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data_from_file(filepath: str) -> pd.DataFrame:
    """Memuat data penjualan dari file CSV."""
    try:
        # Asumsikan format CSV yang sama: kolom pertama adalah pengenal (misalnya Bulan/Tanggal)
        df = pd.read_csv(filepath)
        # Hapus kolom pertama (identifier) dan pastikan semua data yang tersisa adalah numerik
        df_numeric = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').dropna(axis=1)
        return df_numeric
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

# --- Fungsi Prediksi (Diperbarui untuk Menerima DataFrame dinamis) ---
def prediksi_stok_sederhana(
    stok_saat_ini: Dict[str, int],
    safety_stock_faktor: float,
    reorder_point_faktor: float,
    df_penjualan: pd.DataFrame
) -> pd.DataFrame:
    """
    Menghitung rata-rata penjualan, Safety Stock, Reorder Point, dan memberikan rekomendasi.
    """
    
    if df_penjualan.empty:
        # Jika data kosong, kembalikan DataFrame kosong
        return pd.DataFrame() 

    rata_rata_penjualan = df_penjualan.mean().rename('Rata_Rata_Jual')
    df_analisis = pd.DataFrame(rata_rata_penjualan)
    
    # Hitung Safety Stock dan Reorder Point
    df_analisis['Safety_Stock'] = (df_analisis['Rata_Rata_Jual'] * safety_stock_faktor).round().astype(int)
    df_analisis['Reorder_Point'] = (df_analisis['Rata_Rata_Jual'] * reorder_point_faktor).round().astype(int)
    
    # Tambahkan kolom Stok Saat Ini
    # Pastikan hanya kain yang ada di data historis yang dianalisis
    stok_seri = pd.Series({k: stok_saat_ini.get(k, 0) for k in df_analisis.index}, name='Stok_Saat_Ini')
    df_analisis = df_analisis.join(stok_seri)
    
    # Berikan Rekomendasi (sama seperti sebelumnya)
    def get_rekomendasi(row):
        stok_kain = row['Stok_Saat_Ini']
        reorder_p = row['Reorder_Point']
        safety_s = row['Safety_Stock']
        
        if stok_kain <= safety_s:
            return "PERLU SEGERA PESAN ULANG (Stok Kritis!)"
        elif stok_kain <= reorder_p:
            return "Waktunya Pesan Ulang (Dibawah Reorder Point)"
        else:
            return "Stok Aman"
            
    df_analisis['Rekomendasi'] = df_analisis.apply(get_rekomendasi, axis=1)
    
    df_analisis = df_analisis.reset_index().rename(columns={'index': 'Jenis_Kain'})
    
    return df_analisis

# Data Penjualan Global (akan diisi dari file yang diunggah)
# Jika tidak ada file yang diunggah, gunakan data fiktif sederhana sebagai fallback
DATA_PENJUALAN_HISTORIS_GLOBAL = pd.DataFrame()
NAMA_KAIN_GLOBAL = []

# --- Fungsi Fallback Data Fiktif Sederhana (untuk pengguna baru) ---
def get_fallback_data():
    data = {
        'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
        'Kain_A_Batik_Sutera': [50, 55, 60, 48, 52, 65, 70, 68, 72, 58, 62, 75],
        'Kain_B_Katun_Polos': [120, 130, 115, 125, 140, 110, 135, 122, 145, 118, 133, 150],
        'Kain_C_Sutra_Murni': [80, 85, 78, 90, 95, 88, 92, 85, 89, 91, 87, 93],
    }
    df = pd.DataFrame(data).set_index('Bulan')
    return df.iloc[:, :].apply(pd.to_numeric, errors='coerce').dropna(axis=1)


# --- Rute Flask Utama ---
@app.route('/', methods=['GET', 'POST'])
def index():
    global DATA_PENJUALAN_HISTORIS_GLOBAL, NAMA_KAIN_GLOBAL
    
    current_data = DATA_PENJUALAN_HISTORIS_GLOBAL if not DATA_PENJUALAN_HISTORIS_GLOBAL.empty else get_fallback_data()
    NAMA_KAIN_GLOBAL = current_data.columns.tolist()

    default_safety_factor = 0.5
    default_reorder_factor = 1.5
    current_safety_factor = default_safety_factor
    current_reorder_factor = default_reorder_factor
    hasil_prediksi_list = None
    
    # 1. Menangani Unggahan File CSV
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = 'historical_sales_data.csv' 
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Muat dan set data baru secara global
            new_data = load_data_from_file(filepath)
            if not new_data.empty:
                DATA_PENJUALAN_HISTORIS_GLOBAL = new_data
                NAMA_KAIN_GLOBAL = new_data.columns.tolist()
                # Redirect ke halaman yang sama untuk menghindari POST/GET ulang
                return redirect(url_for('index'))
    
    # 2. Menangani Submit Prediksi
    if request.method == 'POST' and 'safety_factor' in request.form:
        # Ambil Input Faktor
        try:
            current_safety_factor = float(request.form.get('safety_factor', default_safety_factor))
            current_reorder_factor = float(request.form.get('reorder_factor', default_reorder_factor))
        except ValueError:
            pass
            
        # Ambil Input Stok
        stok_input = {}
        for kain in NAMA_KAIN_GLOBAL:
            try:
                stok_input[kain] = int(request.form.get(kain, 0))
            except ValueError:
                stok_input[kain] = 0

        # Jalankan Prediksi
        df_hasil = prediksi_stok_sederhana(
            stok_input, 
            current_safety_factor, 
            current_reorder_factor,
            current_data
        )
        
        if not df_hasil.empty:
            hasil_prediksi_list = df_hasil.to_dict('records')
            global LAST_PREDICTION_RESULT
            LAST_PREDICTION_RESULT = df_hasil 
            # ---------------------------
        
    return render_template(
        'index.html', 
        nama_kain=NAMA_KAIN_GLOBAL, 
        hasil=hasil_prediksi_list,
        safety_factor_value=current_safety_factor,
        reorder_factor_value=current_reorder_factor,
        is_custom_data = not DATA_PENJUALAN_HISTORIS_GLOBAL.empty
    )

# Variabel global untuk menyimpan hasil prediksi terakhir
# Ini harus dideklarasikan di bagian atas file Anda, bersama dengan variabel global lainnya
LAST_PREDICTION_RESULT = pd.DataFrame() 

# ... (Pastikan semua kode app.py Anda yang lain ada di sini) ...

@app.route('/download')
def download_file():
    global LAST_PREDICTION_RESULT
    
    if LAST_PREDICTION_RESULT.empty:
        return redirect(url_for('index')) # Kembali ke halaman utama jika belum ada hasil
    
    # Gunakan io.BytesIO untuk membuat buffer di memori
    # Ini memungkinkan kita membuat file Excel tanpa harus menyimpannya ke disk
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Tulis DataFrame hasil ke buffer
    LAST_PREDICTION_RESULT.to_excel(writer, sheet_name='Rekomendasi_Stok', index=False)
    
    # Simpan konten buffer dan pindahkan pointer ke awal
    writer.close()
    output.seek(0)
    
    # Kirim file ke browser
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='Prediksi_Stok_Kain.xlsx', # Nama file yang akan diunduh pengguna
        as_attachment=True
    )
if __name__ == '__main__':
    # Untuk menjalankan di lingkungan lokal:
    app.run(debug=True) 