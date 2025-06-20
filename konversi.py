import pandas as pd
import json
import os

# --- KONFIGURASI ---
# Pastikan nama file ini sesuai dengan file CSV Anda
csv_file_path = 'data_keluarga.csv'

# Folder ini akan dibuat untuk menyimpan semua file JSON
output_folder = 'hasil_json'

# --- NAMA KOLOM KUNCI (SESUAIKAN JIKA PERLU) ---
# Jika nama kolom untuk Nomor KK di file Anda berbeda, ubah di sini.
# Contoh: Jika nama kolomnya 'NOMOR KARTU KELUARGA', ubah baris di bawah.
KOLOM_NOMOR_KK = 'NO KK'


def konversi_csv_ke_json(path_csv, folder_output):
    try:
        # 1. Membaca file CSV
        try:
            df = pd.read_csv(path_csv, encoding='utf-8', dtype=str)
            print("File CSV berhasil dibaca dengan encoding UTF-8.")
        except UnicodeDecodeError:
            print("Gagal membaca dengan UTF-8. Mencoba dengan encoding 'latin1'...")
            df = pd.read_csv(path_csv, encoding='latin1', dtype=str)
            print("File CSV berhasil dibaca dengan encoding 'latin1'.")

        # 2. Membersihkan nama kolom untuk mencegah KeyError
        print("\nNama kolom asli:", list(df.columns))
        df.columns = df.columns.str.strip().str.upper()
        print("Nama kolom setelah dibersihkan:", list(df.columns))

        # 3. Validasi apakah kolom KK ada setelah pembersihan
        if KOLOM_NOMOR_KK not in df.columns:
            print(f"\n--- ERROR KRITIS ---")
            print(f"Kolom '{KOLOM_NOMOR_KK}' tidak ditemukan di file CSV Anda.")
            print(f"Pastikan nama kolom sudah benar atau sesuaikan variabel 'KOLOM_NOMOR_KK' di dalam skrip.")
            return

        # 4. Membersihkan data
        # Mengisi nilai kosong (NaN) dengan string kosong
        df.fillna('', inplace=True)
        print("\nPembersihan data selesai.")

        # 5. Membuat folder output jika belum ada
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
            print(f"Folder '{folder_output}' berhasil dibuat.")

        # 6. Mengelompokkan data berdasarkan Nomor KK
        grup_kk = df.groupby(KOLOM_NOMOR_KK)
        
        jumlah_file = 0
        print("\nMemulai proses konversi...")

        # 7. Iterasi dan pembuatan file JSON
        for no_kk, data_keluarga in grup_kk:
            if not no_kk: continue # Lewati jika nomor KK kosong
            anggota_pertama = data_keluarga.iloc[0]

            json_final = {
                "kk": no_kk,
                "alamatLengkap": {
                    "alamat": anggota_pertama.get('ALAMAT', ''), "rt": anggota_pertama.get('RT', ''),
                    "rw": anggota_pertama.get('RW', ''), "kelurahan": anggota_pertama.get('KELURAHAN', ''),
                    "kecamatan": anggota_pertama.get('KECAMATAN', ''), "kabupaten": anggota_pertama.get('KABUPATEN', ''),
                    "provinsi": anggota_pertama.get('PROVINSI', ''), "kodePos": anggota_pertama.get('KODE POS', '')
                },
                "anggota": []
            }

            for _, anggota in data_keluarga.iterrows():
                try:
                    tgl_lahir_obj = pd.to_datetime(anggota.get('TANGGAL LAHIR', ''), dayfirst=True)
                    tgl_lahir_str = tgl_lahir_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    tgl_lahir_str = None

                json_final["anggota"].append({
                    "nik": anggota.get('NIK', ''), "namaLengkap": anggota.get('NAMA', ''),
                    "jenisKelamin": anggota.get('JENIS KELAMIN', ''), "tempatLahir": anggota.get('TEMPAT LAHIR', ''),
                    "tanggalLahir": tgl_lahir_str, "agama": anggota.get('AGAMA', ''),
                    "pendidikan": anggota.get('PENDIDIKAN', ''), "jenisPekerjaan": anggota.get('PEKERJAAN', ''),
                    "statusPernikahan": anggota.get('STATUS PERNIKAHAN', ''),
                    "statusHubunganKeluarga": anggota.get('HUBUNGAN KELUARGA', ''),
                    "kewarganegaraan": anggota.get('KEWARGANEGARAAN', ''), "wallet": None
                })

            path_file_json = os.path.join(folder_output, f"{no_kk}.json")
            with open(path_file_json, 'w', encoding='utf-8') as f:
                json.dump(json_final, f, ensure_ascii=False, indent=2)
            
            jumlah_file += 1
        
        print(f"\nPROSES SELESAI! Total {jumlah_file} file JSON telah dibuat di folder '{folder_output}'.")

    except FileNotFoundError:
        print(f"ERROR: File '{path_csv}' tidak ditemukan. Pastikan file berada di folder yang sama dengan skrip.")
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")

if __name__ == "__main__":
    konversi_csv_ke_json(csv_file_path, output_folder)