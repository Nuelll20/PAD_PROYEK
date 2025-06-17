import pandas as pd

class DataHandler:
    #Kelas untuk membaca dan menyimpan data penjualan.
    def __init__(self):
        self.data = None

    def load_csv(self, filepath):
        #Load file CSV, parsing kolom tanggal ke datetime.
        try:
            df = pd.read_csv(filepath, parse_dates=['tanggal'])
            # Validasi kolom
            expected = {'tanggal','produk','jumlah_terjual','harga_satuan'}
            if not expected.issubset(df.columns):
                raise ValueError(f"CSV harus memiliki kolom: {expected}")
            self.data = df
            return True, None
        except Exception as e:
            return False, str(e)

    def get_data(self):
        #Mengembalikan DataFrame yang telah di-load.
        return self.data
