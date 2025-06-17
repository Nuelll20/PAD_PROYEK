import pandas as pd

class SalesAnalyzer:
    """Kelas untuk analisis data penjualan."""

    def __init__(self, data: pd.DataFrame):
        """
        Inisialisasi analyzer dengan DataFrame yang sudah memiliki:
        - tanggal (datetime)
        - produk (string)
        - jumlah_terjual (int)
        - harga_satuan (int/float)
        """
        self.data = data.copy()
        self.data['pendapatan'] = self.data['jumlah_terjual'] * self.data['harga_satuan']

    def total_sales_per_product(self):
        """Hitung total unit terjual per produk."""
        return self.data.groupby('produk')['jumlah_terjual'] \
                        .sum().sort_values(ascending=False)

    def total_income_per_product(self):
        """Hitung total pendapatan per produk."""
        return self.data.groupby('produk')['pendapatan'] \
                        .sum().sort_values(ascending=False)

    def daily_income(self):
        """Total pendapatan per tanggal (series indexed by tanggal)."""
        return self.data.groupby('tanggal')['pendapatan'] \
                        .sum().sort_index()

    def monthly_income(self):
        """Total pendapatan per bulan (series indexed by periode 'YYYY-MM')."""
        df = self.data.copy()
        df['bulan'] = df['tanggal'].dt.to_period('M')
        return df.groupby('bulan')['pendapatan'].sum().sort_index()

    def top_selling_product(self):
        """
        Produk dengan penjualan unit terbanyak.
        Mengembalikan tuple: (nama produk, total unit).
        """
        ts = self.total_sales_per_product()
        if ts.empty:
            return (None, 0)
        return ts.index[0], ts.iloc[0]

    def avg_daily_sales(self):
        """Rata-rata unit terjual per hari."""
        daily = self.data.groupby('tanggal')['jumlah_terjual'].sum()
        return daily.mean() if not daily.empty else 0

    def sales_summary(self):
        """
        Ringkasan data penjualan:
        - transactions: jumlah baris
        - units: total unit terjual
        - income: total pendapatan
        """
        return {
            'transactions': len(self.data),
            'units': self.data['jumlah_terjual'].sum(),
            'income': self.data['pendapatan'].sum()
        }
