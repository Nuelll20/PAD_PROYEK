import pandas as pd

class DataHandler:
    def __init__(self):
        self.data = pd.DataFrame()

    def load_csv(self, path):
        try:
            df = pd.read_csv(path)
            df.columns = [c.strip().lower() for c in df.columns]

            # Pastikan kolom wajib ada
            required_cols = ['tanggal', 'produk', 'jumlah_terjual', 'harga_satuan']
            for col in required_cols:
                if col not in df.columns:
                    return False, f"Kolom '{col}' tidak ditemukan dalam CSV."

            # Konversi dan hitung pendapatan
            df['tanggal'] = pd.to_datetime(df['tanggal'], format='%d/%m/%y', errors='coerce')
            df['jumlah_terjual'] = pd.to_numeric(df['jumlah_terjual'], errors='coerce')
            df['harga_satuan'] = pd.to_numeric(df['harga_satuan'], errors='coerce')
            df['pendapatan'] = df['jumlah_terjual'] * df['harga_satuan']
            df.dropna(subset=['tanggal', 'jumlah_terjual', 'harga_satuan'], inplace=True)
            # Tambahan validasi: pastikan masih ada data dan tanggal valid
            if df.empty or df['tanggal'].isnull().all():
                return False, "Data kosong atau tidak ada tanggal yang valid setelah parsing."
            self.data = df
            return True, "Sukses"
        except Exception as e:
            return False, str(e)

    def get_data(self):
        return self.data.copy()
