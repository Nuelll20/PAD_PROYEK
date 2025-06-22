class SalesAnalyzer:
    def __init__(self, df):
        self.data = df.copy()

    def total_sales_per_product(self):
        return self.data.groupby('produk')['jumlah_terjual'].sum().sort_values(ascending=False)

    def total_income_per_product(self):
        return self.data.groupby('produk')['pendapatan'].sum().sort_values(ascending=False)

    def daily_income(self):
        return self.data.groupby('tanggal')['pendapatan'].sum().sort_index()

    def monthly_income(self):
        return self.data.groupby(self.data['tanggal'].dt.to_period("M"))['pendapatan'].sum().sort_index()

    def top_selling_product(self):
        s = self.total_sales_per_product()
        if s.empty:
            return "-", 0
        return s.index[0], s.iloc[0]

    def avg_daily_sales(self):
        return self.data.groupby('tanggal')['jumlah_terjual'].sum().mean()

    def sales_summary(self):
        return {
            "transactions": len(self.data),
            "units": int(self.data['jumlah_terjual'].sum()),
            "income": int(self.data['pendapatan'].sum())
        }
