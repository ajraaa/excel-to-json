import pandas as pd
import json
import os

# --- KONFIGURASI ---
csv_file_path = 'data_keluarga.csv'
output_folder = 'hasil_json'

# --- NAMA KOLOM KUNCI (SESUAIKAN JIKA NAMA DI CSV BERBEDA) ---
KOLOM_NOMOR_KK = 'NO KK'

def konversi_final(path_csv, folder_output):
    """
    Fungsi definitif yang membaca CSV dan mengonversinya ke JSON
    sesuai dengan skema yang telah diberikan secara lengkap.
    """
    try:
        # 1. Membaca file CSV
        # dtype=str untuk memastikan NIK, KK, dll tidak kehilangan angka 0 di depan
        try:
            df = pd.read_csv(path_csv, encoding='utf-8', dtype=str)
            print("File CSV berhasil dibaca dengan encoding UTF-8.")
        except UnicodeDecodeError:
            print("Gagal membaca dengan UTF-8. Mencoba dengan encoding 'latin1'...")
            df = pd.read_csv(path_csv, encoding='latin1', dtype=str)
            print("File CSV berhasil dibaca dengan encoding 'latin1'.")

        # 2. Membersihkan nama kolom
        df.columns = df.columns.str.strip().str.upper()
        print("Nama kolom setelah dibersihkan:", list(df.columns))

        # 3. Validasi kolom KK
        if KOLOM_NOMOR_KK not in df.columns:
            print(f"\n--- ERROR KRITIS ---")
            print(f"Kolom '{KOLOM_NOMOR_KK}' tidak ditemukan di file CSV.")
            return

        # 4. Membersihkan data
        df.fillna('', inplace=True)
        print("\nPembersihan data dan memulai proses konversi...")

        # 5. Membuat folder output
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
            print(f"Folder '{folder_output}' berhasil dibuat.")

        # 6. Mengelompokkan data
        grup_kk = df.groupby(KOLOM_NOMOR_KK)
        
        jumlah_file = 0
        
        # 7. Iterasi dan pembuatan file JSON
        for no_kk, data_keluarga in grup_kk:
            if not no_kk: continue
            anggota_pertama = data_keluarga.iloc[0]

            # Konversi 'versi' ke integer, default ke 0 jika error
            try:
                versi_int = int(float(anggota_pertama.get('VERSI', 0)))
            except (ValueError, TypeError):
                versi_int = 0

            # Konversi 'Waktu Upload' ke format date-time ISO 8601 jika memungkinkan
            try:
                waktu_upload_obj = pd.to_datetime(anggota_pertama.get('WAKTU UPLOAD', ''))
                waktu_upload_str = waktu_upload_obj.isoformat()
            except (ValueError, TypeError):
                waktu_upload_str = anggota_pertama.get('WAKTU UPLOAD', '')


            json_final = {
                "kk": no_kk,
                "alamatLengkap": {
                    "alamat": anggota_pertama.get('ALAMAT', ''),
                    "rt": anggota_pertama.get('RT', ''),
                    "rw": anggota_pertama.get('RW', ''),
                    "kelurahan": anggota_pertama.get('KELURAHAN', ''),
                    "kecamatan": anggota_pertama.get('KECAMATAN', ''),
                    "kabupaten": anggota_pertama.get('KABUPATEN', ''),
                    "provinsi": anggota_pertama.get('PROVINSI', ''),
                    "kodePos": anggota_pertama.get('KODE POS', '')
                },
                "anggota": [],
                # --- MENAMBAHKAN FIELD SESUAI SKEMA LENGKAP ---
                "diunggahOleh": anggota_pertama.get('DIUNGGAH OLEH', ''),
                "waktuUpload": waktu_upload_str,
                "versi": versi_int
            }

            for _, anggota in data_keluarga.iterrows():
                try:
                    tgl_lahir_obj = pd.to_datetime(anggota.get('TANGGAL LAHIR', ''), dayfirst=True)
                    tgl_lahir_str = tgl_lahir_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    tgl_lahir_str = None

                json_final["anggota"].append({
                    "nik": anggota.get('NIK', ''),
                    "nama": anggota.get('NAMA', ''),
                    "jenisKelamin": anggota.get('JENIS KELAMIN', ''),
                    "tempatLahir": anggota.get('TEMPAT LAHIR', ''),
                    "tanggalLahir": tgl_lahir_str,
                    "agama": anggota.get('AGAMA', ''),
                    "pendidikan": anggota.get('PENDIDIKAN', ''),
                    "jenisPekerjaan": anggota.get('PEKERJAAN', ''),
                    "statusPernikahan": anggota.get('STATUS PERNIKAHAN', ''),
                    "statusHubunganKeluarga": anggota.get('HUBUNGAN KELUARGA', ''),
                    "kewarganegaraan": anggota.get('KEWARGANEGARAAN', ''),
                    "wallet": anggota.get('WALLET', None) or None
                })

            path_file_json = os.path.join(folder_output, f"{no_kk}.json")
            with open(path_file_json, 'w', encoding='utf-8') as f:
                json.dump(json_final, f, ensure_ascii=False, indent=2)
            
            jumlah_file += 1
        
        print(f"\nPROSES SELESAI! Total {jumlah_file} file JSON telah dibuat.")

    except FileNotFoundError:
        print(f"ERROR: File '{path_csv}' tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")

if __name__ == "__main__":
    konversi_final(csv_file_path, output_folder)