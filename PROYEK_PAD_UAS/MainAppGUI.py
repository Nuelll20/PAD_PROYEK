import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from data_handler import DataHandler
from sales_analyzer import SalesAnalyzer

class MainAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Toko Baju XYZ – Sales Dashboard")
        self.root.geometry("1100x720")
        self.dh = DataHandler()
        self.sa = None
        self.current_fig = None

        self.setup_style()
        self.build_header()
        self.build_controls()
        self.build_stats()
        self.build_notebook()

    def setup_style(self):
        s = ttk.Style(self.root)
        s.theme_use('alt')
        bg = '#f0f2f5'
        panel = '#ffffff'
        txt = '#333'
        accent = '#1abc9c'
        hover = '#16a085'

        self.root.configure(bg=bg)
        s.configure('TFrame', background=bg)
        s.configure('Paneled.TFrame', background=panel, relief='groove', borderwidth=1)
        s.configure('Header.TLabel', background=bg, foreground=txt, font=('Segoe UI Semibold', 18))
        s.configure('StatHeader.TLabel',
                    background=panel, foreground=txt,
                    font=('Segoe UI Semibold', 11, 'bold'))
        s.configure('StatValue.TLabel',
                    background=panel, foreground=txt,
                    font=('Segoe UI Semibold', 11))
        s.configure('Accent.TButton',
                    background=accent, foreground='white',
                    font=('Segoe UI Semibold', 10),
                    padding=6, borderwidth=0)
        s.map('Accent.TButton', background=[('active', hover)])
        s.configure('TCombobox', padding=3)

    def build_header(self):
        header = ttk.Frame(self.root, style= 'TFrame')
        header.pack(fill=tk.X, padx=10, pady=(10,5))
        img = ImageTk.PhotoImage(Image.open("icons/shop.png").resize((60,60)))
        ttk.Label(header, image=img).grid(row=0, column=0, padx=5)
        ttk.Label(header, text="Laporan Penjualan", style= 'Header.TLabel').grid(row=0, column=1)
        self.shop_img = img

    def build_controls(self):
        ctrl = ttk.Frame(self.root, style= 'TFrame')
        ctrl.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(ctrl, text="Dari tanggal:").grid(row=0, column=0, padx=5)
        self.cal_start = DateEntry(ctrl, date_pattern='dd/MM/yyyy', width=12)
        self.cal_start.grid(row=0, column=1, padx=5)
        ttk.Label(ctrl, text="Sampai tanggal:").grid(row=0, column=2, padx=5)
        self.cal_end = DateEntry(ctrl, date_pattern='dd/MM/yyyy', width=12)
        self.cal_end.grid(row=0, column=3, padx=5)  
        ctrl.grid_columnconfigure(5, weight=1)  
        self.cal_start.bind("<<DateEntrySelected>>", lambda e: self.refresh_date_filter())
        self.cal_end.bind("<<DateEntrySelected>>", lambda e: self.refresh_date_filter())

        upload = ImageTk.PhotoImage(Image.open("icons/upload.png").resize((20,20)))
        self.btn_load = ttk.Button(ctrl, image=upload, text=" Load CSV", style= 'Accent.TButton',
                                   compound='left', command=self.load_data)
        self.btn_load.grid(row=0, column=4, padx=10, ipadx=5)
        self.upload = upload

        self.analysis_var = tk.StringVar()
        self.analysis_menu = ttk.Combobox(ctrl, textvariable=self.analysis_var,
            state='readonly',
            values=[
                    "Total penjualan per produk",
                    "Total pendapatan per produk",
                    "Pendapatan harian",
                    "Pendapatan bulanan",
                    "Proporsi produk",
                    "Produk terlaris",
                    "Rata-rata penjualan harian"
                    ])
        self.analysis_menu.grid(row=0, column=5, padx=5, sticky='ew')
        self.analysis_menu.bind("<<ComboboxSelected>>", lambda e: self.show_analysis())

        self.btn_export_csv = ttk.Button(ctrl, text="Export CSV",
            style='Accent.TButton',
            command=self.export_csv)
        self.btn_export_csv.grid(row=0, column=6, padx=5, ipadx=5)
        self.btn_export_chart = ttk.Button(ctrl, text="Export Chart",
            style='Accent.TButton',
            command=self.export_chart)
        self.btn_export_chart.grid(row=0, column=7, padx=5)

    def build_stats(self):
        stats = ttk.Frame(self.root, style='Paneled.TFrame')
        stats.pack(fill=tk.X, padx=10, pady=5)

        headers = ["Transaksi", "Total Unit", "Total Pendapatan", "Produk Terlaris"]
        for col, hdr in enumerate(headers):
            ttk.Label(stats, text=hdr, style='StatHeader.TLabel').grid(row=0, column=col*2, padx=10, pady=(4,2))
            if col < len(headers)-1:
                sep = ttk.Separator(stats, orient='vertical')
                sep.grid(row=0, column=col*2+1, rowspan=2, sticky='ns', padx=5)

        self.lbl_tx = ttk.Label(stats, text="0", style='StatValue.TLabel', anchor='center')
        self.lbl_units = ttk.Label(stats, text="0", style='StatValue.TLabel', anchor='center')
        self.lbl_total_income = ttk.Label(stats, text="Rp 0", style='StatValue.TLabel', anchor='center')
        self.lbl_top_product = ttk.Label(stats, text="-", style='StatValue.TLabel', anchor='center')

        self.lbl_tx.grid(row=1, column=0, padx=10, pady=(0,4), sticky='ew')
        self.lbl_units.grid(row=1, column=2, padx=10, pady=(0,4), sticky='ew')
        self.lbl_total_income.grid(row=1, column=4, padx=10, pady=(0,4), sticky='ew')
        self.lbl_top_product.grid(row=1, column=6, padx=10, pady=(0,4), sticky='ew')

        # Pastikan semua kolom sama lebar supaya seimbang
        for i in range(0, len(headers)*2 - 1, 2):
            stats.grid_columnconfigure(i, weight=1)
        
    def build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5,10))

        self.tab_dash = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dash, text="Dashboard")
        self.canvas_frame = ttk.Frame(self.tab_dash, style='Paneled.TFrame')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text="Laporan")
        cols = [("tanggal","Tanggal",100),("produk","Produk",200),
                ("jumlah","Jumlah",80),("harga","Harga",100),("pendapatan","Pendapatan",120)]
        self.tree = ttk.Treeview(self.tab_report, columns=[c[0] for c in cols], show='headings')
        for c, t, w in cols:
            self.tree.heading(c, text=t); self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return
        ok, msg = self.dh.load_csv(path)
        if not ok:
            return messagebox.showerror("Error", f"Gagal load CSV:\n{msg}")

        self.sa = SalesAnalyzer(self.dh.get_data())
        self.cal_start.set_date(self.sa.data['tanggal'].min())
        self.cal_end.set_date(self.sa.data['tanggal'].max())
        self.refresh_date_filter()
        self.analysis_menu.current(0)
        self.show_analysis()

    def refresh_date_filter(self):
        if not self.sa: return
        df0 = self.dh.get_data()
        start = pd.to_datetime(self.cal_start.get_date())
        end = pd.to_datetime(self.cal_end.get_date())
        df = df0[(df0['tanggal'] >= start) & (df0['tanggal'] <= end)]
        self.sa = SalesAnalyzer(df)
        self.show_analysis()

    def show_analysis(self):
        for w in self.canvas_frame.winfo_children(): 
            w.destroy()
        if not self.sa or self.sa.data.empty: 
            return

        kind = self.analysis_var.get()
        fig, ax = plt.subplots(figsize=(8, 4))
        
        if kind == "Total penjualan per produk":
            s = self.sa.total_sales_per_product()
            cmap = plt.get_cmap('Blues')
            colors = cmap(np.linspace(0.4, 0.9, len(s)))
            ax.bar(s.index, s.values, color=colors)
            ax.set_title("Jumlah Terjual per Produk")
        elif kind == "Total pendapatan per produk":
            s = self.sa.total_income_per_product()
            cmap = plt.get_cmap('Greens')
            colors = cmap(np.linspace(0.4, 0.9, len(s)))
            ax.bar(s.index, s.values, color=colors)
            ax.set_title("Pendapatan per Produk")
        elif kind == "Pendapatan harian":
            s = self.sa.daily_income()
            norm = plt.Normalize(vmin=s.values.min(), vmax=s.values.max())
            cmap = plt.get_cmap('viridis')
            line_colors = cmap(norm(s.values))
            ax.plot(s.index, s.values, marker='o', color='blue')
            for i in range(len(s.index)-1):
                ax.plot(s.index[i:i+2], s.values[i:i+2], color=line_colors[i])
            ax.set_title("Pendapatan Harian")
        elif kind == "Pendapatan bulanan":
            s = self.sa.monthly_income()
            bars = ax.bar(s.index.astype(str), s.values, color='#e67e22')
            ax.set_title("Pendapatan per Bulan")
            for b, val in zip(bars, s.values):
                ax.text(b.get_x() + b.get_width()/2, val*1.01,
                        f"Rp {val:,.0f}", ha='center', va='bottom', fontsize=9)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        elif kind == "Proporsi produk":
            s = self.sa.total_sales_per_product()
            s.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title("Proporsi Penjualan per Produk")
            
        elif kind == "Produk terlaris":
            prod, qty = self.sa.top_selling_product()
            ax.bar([prod], [qty], color='orange')
            ax.set_title(f"Produk Terlaris: {prod} ({qty} unit)")
        elif kind == "Rata-rata penjualan harian":
            daily = self.sa.data.groupby('tanggal')['jumlah_terjual'].sum().sort_index()
            avg = self.sa.avg_daily_sales()
            norm = plt.Normalize(vmin=daily.min(), vmax=daily.max())
            cmap = plt.get_cmap('viridis')
            line_colors = cmap(norm(daily.values))
            for i in range(len(daily)-1):
                ax.plot(daily.index[i:i+2], daily.values[i:i+2], color=line_colors[i], marker='o')
            ax.hlines(avg, daily.index.min(), daily.index.max(),
                      colors='green', linestyle='--', label=f'Rata-rata: {avg:.2f}')
            ax.set_title("Poligon Penjualan Harian")
            ax.set_ylabel("Unit Terjual")
            ax.legend()
        else:
            return

        ax.set_ylabel("Jumlah")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_fig = fig
        self.update_stats()
        self.populate_report()

    def update_stats(self):
        summ = self.sa.sales_summary()
        prod, qty = self.sa.top_selling_product()
        self.lbl_tx.config(text=f"Transaksi: {summ['transactions']}")
        self.lbl_units.config(text=f"Total Unit: {summ['units']}")
        self.lbl_total_income.config(text=f"Total Pendapatan: Rp {summ['income']:,}")
        self.lbl_top_product.config(text=f"Produk Terlaris: {prod} ({qty} unit)")

    def populate_report(self):
        self.tree.delete(*self.tree.get_children())
        for _, r in self.sa.data.iterrows():
            self.tree.insert("", "end", values=(
                r['tanggal'].strftime("%d/%m/%Y"),
                r['produk'],
                r['jumlah_terjual'],
                f"{r['harga_satuan']:,}",
                f"{r['pendapatan']:,}"
            ))

    def export_csv(self):
        if not self.sa: return messagebox.showwarning("Peringatan", "Belum load data!")
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file","*.csv")])
        if path:
            self.sa.data.to_csv(path, index=False)
            messagebox.showinfo("Sukses", f"CSV tersimpan:\n{path}")

    def export_chart(self):
        if not self.current_fig: return messagebox.showwarning("Peringatan", "Belum ada grafik untuk diekspor")
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image","*.png")])
        if path:
            self.current_fig.savefig(path, dpi=150)
            messagebox.showinfo("Sukses", f"Grafik tersimpan:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    MainAppGUI(root)
    root.mainloop()
