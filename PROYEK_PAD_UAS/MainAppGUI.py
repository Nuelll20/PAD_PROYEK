import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from data_handler import DataHandler
from sales_analyzer import SalesAnalyzer

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from data_handler import DataHandler
from sales_analyzer import SalesAnalyzer

class MainAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Toko Baju XYZ – Dasbor Penjualan")
        self.root.geometry("1100x720")
        self.pengelola_data = DataHandler()
        self.penganalisis_penjualan = None
        self.grafik_aktif = None

        self.atur_gaya()
        self.build_header()
        self.build_kontrol()
        self.build_statistik()
        self.build_notebook()

    def atur_gaya(self):
        gaya = ttk.Style(self.root)
        gaya.theme_use('alt')
        latar = '#f0f2f5'
        panel = '#ffffff'
        teks = '#333'
        aksen = '#1abc9c'
        hover = '#16a085'

        self.root.configure(bg=latar)
        gaya.configure('TFrame', background=latar)
        gaya.configure('Paneled.TFrame', background=panel, relief='groove', borderwidth=1)
        gaya.configure('Header.TLabel', background=latar, foreground=teks, font=('Segoe UI Semibold', 18))
        gaya.configure('StatHeader.TLabel', background=panel, foreground=teks, font=('Segoe UI Semibold', 11, 'bold'))
        gaya.configure('StatValue.TLabel', background=panel, foreground=teks, font=('Segoe UI Semibold', 11))
        gaya.configure('Accent.TButton', background=aksen, foreground='white', font=('Segoe UI Semibold', 10), padding=6, borderwidth=0)
        gaya.map('Accent.TButton', background=[('active', hover)])
        gaya.configure('TCombobox', padding=3)

    def build_header(self):
        header = ttk.Frame(self.root, style='TFrame')
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        try:
            gambar = ImageTk.PhotoImage(Image.open("icons/shop.png").resize((60, 60)))
        except Exception as e:
            messagebox.showwarning("Kesalahan Gambar", f"Gagal memuat ikon: {e}")
            gambar = None

        if gambar:
            ttk.Label(header, image=gambar).grid(row=0, column=0, padx=5)
            self.shop_img = gambar
        ttk.Label(header, text="Laporan Penjualan", style='Header.TLabel').grid(row=0, column=1)

    def build_kontrol(self):
        kontrol = ttk.Frame(self.root, style='TFrame')
        kontrol.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(kontrol, text="Dari tanggal:").grid(row=0, column=0, padx=5)
        self.kal_awal = DateEntry(kontrol, date_pattern='dd/MM/yyyy', width=12)
        self.kal_awal.grid(row=0, column=1, padx=5)
        ttk.Label(kontrol, text="Sampai tanggal:").grid(row=0, column=2, padx=5)
        self.kal_akhir = DateEntry(kontrol, date_pattern='dd/MM/yyyy', width=12)
        self.kal_akhir.grid(row=0, column=3, padx=5)

        kontrol.grid_columnconfigure(5, weight=1)
        self.kal_awal.bind("<<DateEntrySelected>>", lambda e: self.perbarui_filter_tanggal())
        self.kal_akhir.bind("<<DateEntrySelected>>", lambda e: self.perbarui_filter_tanggal())

        try:
            ikon_upload = ImageTk.PhotoImage(Image.open("icons/upload.png").resize((20, 20)))
        except Exception as e:
            messagebox.showwarning("Kesalahan Gambar", f"Gagal memuat ikon upload: {e}")
            ikon_upload = None

        self.tombol_muat = ttk.Button(kontrol, image=ikon_upload, text=" Muat CSV", style='Accent.TButton',
                                      compound='left', command=self.muat_data)
        self.tombol_muat.grid(row=0, column=4, padx=10, ipadx=5)
        self.upload = ikon_upload

        self.variabel_analisis = tk.StringVar()
        self.menu_analisis = ttk.Combobox(kontrol, textvariable=self.variabel_analisis,
            state='readonly',
            values=[
                "Total penjualan per produk",
                "Total pendapatan per produk",
                "Pendapatan harian",
                "Pendapatan bulanan",
                "Proporsi produk",
                "Produk terlaris",
                "Rata-rata penjualan harian"])
        self.menu_analisis.grid(row=0, column=5, padx=5, sticky='ew')
        self.menu_analisis.bind("<<ComboboxSelected>>", lambda e: self.tampilkan_analisis())

        self.tombol_ekspor_csv = ttk.Button(kontrol, text="Ekspor CSV", style='Accent.TButton', command=self.ekspor_csv)
        self.tombol_ekspor_csv.grid(row=0, column=6, padx=5, ipadx=5)

        self.tombol_ekspor_grafik = ttk.Button(kontrol, text="Ekspor Grafik", style='Accent.TButton', command=self.ekspor_grafik)
        self.tombol_ekspor_grafik.grid(row=0, column=7, padx=5)

    def build_statistik(self):
        statistik = ttk.Frame(self.root, style='Paneled.TFrame')
        statistik.pack(fill=tk.X, padx=10, pady=5)
        header = ["Transaksi", "Total Unit", "Total Pendapatan", "Produk Terlaris"]
        for kolom, judul in enumerate(header):
            ttk.Label(statistik, text=judul, style='StatHeader.TLabel').grid(row=0, column=kolom*2, padx=10, pady=(4, 2))
            if kolom < len(header) - 1:
                ttk.Separator(statistik, orient='vertical').grid(row=0, column=kolom*2+1, rowspan=2, sticky='ns', padx=5)

        self.label_tx = ttk.Label(statistik, text="0", style='StatValue.TLabel')
        self.label_unit = ttk.Label(statistik, text="0", style='StatValue.TLabel')
        self.label_pendapatan = ttk.Label(statistik, text="Rp 0", style='StatValue.TLabel')
        self.label_produk_terlaris = ttk.Label(statistik, text="-", style='StatValue.TLabel')

        self.label_tx.grid(row=1, column=0, pady=(0, 4))
        self.label_unit.grid(row=1, column=2, pady=(0, 4))
        self.label_pendapatan.grid(row=1, column=4, pady=(0, 4))
        self.label_produk_terlaris.grid(row=1, column=6, pady=(0, 4))

    def build_notebook(self):
        self.buku_catatan = ttk.Notebook(self.root)
        self.buku_catatan.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        self.tab_beranda = ttk.Frame(self.buku_catatan)
        self.buku_catatan.add(self.tab_beranda, text="Dasbor")
        self.kanvas_frame = ttk.Frame(self.tab_beranda, style='Paneled.TFrame')
        self.kanvas_frame.pack(fill=tk.BOTH, expand=True)

        self.tab_laporan = ttk.Frame(self.buku_catatan)
        self.buku_catatan.add(self.tab_laporan, text="Laporan")
        kolom = [("tanggal", "Tanggal", 100), ("produk", "Produk", 200),
                 ("jumlah", "Jumlah", 80), ("harga", "Harga", 100), ("pendapatan", "Pendapatan", 120)]
        self.tabel_pohon = ttk.Treeview(self.tab_laporan, columns=[k[0] for k in kolom], show='headings')
        for nama, teks, lebar in kolom:
            self.tabel_pohon.heading(nama, text=teks)
            self.tabel_pohon.column(nama, width=lebar)
        self.tabel_pohon.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def muat_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        berhasil, pesan = self.pengelola_data.load_csv(path)
        if not berhasil:
            messagebox.showerror("Kesalahan", f"Gagal memuat CSV:\n{pesan}")
            return

        self.penganalisis_penjualan = SalesAnalyzer(self.pengelola_data.get_data())

        tanggal_min = self.penganalisis_penjualan.data['tanggal'].min()
        tanggal_max = self.penganalisis_penjualan.data['tanggal'].max()

        #Validasi nilai tanggal agar tidak menyebabkan error di set_date()
        if pd.isnull(tanggal_min) or pd.isnull(tanggal_max):
            messagebox.showerror("Kesalahan", "Tidak dapat menentukan rentang tanggal karena data tanggal tidak valid.")
            return

        self.kal_awal.set_date(tanggal_min)
        self.kal_akhir.set_date(tanggal_max)
        self.perbarui_filter_tanggal()
        self.menu_analisis.current(0)
        self.tampilkan_analisis()

    def perbarui_filter_tanggal(self):
        if not self.penganalisis_penjualan:
            return
        data_asli = self.pengelola_data.get_data()
        awal = pd.to_datetime(self.kal_awal.get_date())
        akhir = pd.to_datetime(self.kal_akhir.get_date())

        if akhir < awal:
            messagebox.showwarning("Peringatan", "Tanggal akhir tidak boleh sebelum tanggal awal.")
            return

        data_terfilter = data_asli[(data_asli['tanggal'] >= awal) & (data_asli['tanggal'] <= akhir)]

        if data_terfilter.empty:
            messagebox.showinfo("Informasi", "Tidak ada data dalam rentang tanggal yang dipilih.")

        self.penganalisis_penjualan = SalesAnalyzer(data_terfilter)
        self.tampilkan_analisis()

    def tampilkan_analisis(self):
        for widget in self.kanvas_frame.winfo_children():
            widget.destroy()
        if not self.penganalisis_penjualan or self.penganalisis_penjualan.data.empty:
            return

        jenis = self.variabel_analisis.get()
        fig, ax = plt.subplots(figsize=(8, 4))

        if getattr(self, 'tema_gelap', False):
            fig.patch.set_facecolor('#34495e')
            ax.set_facecolor('#34495e')
            ax.tick_params(colors='#ecf0f1')
            ax.title.set_color('#ecf0f1')
            ax.xaxis.label.set_color('#ecf0f1')
            ax.yaxis.label.set_color('#ecf0f1')
            for spine in ax.spines.values():
                spine.set_color('#ecf0f1')
        else:
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            ax.tick_params(colors='#333')
            ax.title.set_color('#333')
            ax.xaxis.label.set_color('#333')
            ax.yaxis.label.set_color('#333')
            for spine in ax.spines.values():
                spine.set_color('#333')

        animasi = None
        sa = self.penganalisis_penjualan

        if jenis == "Total penjualan per produk":
            data = sa.total_sales_per_product()
            warna = plt.get_cmap('Blues')(np.linspace(0.4, 0.9, len(data)))
            ax.set_ylim(0, max(data.values) * 1.1)
            animasi = self.animasi_grafik(fig, ax, data.index, data.values, kind='bar', color=warna)
            ax.set_title("Jumlah Terjual per Produk")
        elif jenis == "Total pendapatan per produk":
            data = sa.total_income_per_product()
            warna = plt.get_cmap('Greens')(np.linspace(0.4, 0.9, len(data)))
            ax.set_ylim(0, max(data.values) * 1.1)
            animasi = self.animasi_grafik(fig, ax, data.index, data.values, kind='bar', color=warna)
            ax.set_title("Pendapatan per Produk")
        elif jenis == "Pendapatan harian":
            data = sa.daily_income()
            ax.set_ylim(0, max(data.values) * 1.1)
            animasi = self.animasi_grafik(fig, ax, data.index, data.values, kind='bar', color='deepskyblue')
            ax.set_title("Pendapatan Harian")
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        elif jenis == "Pendapatan bulanan":
            data = sa.monthly_income()
            ax.set_ylim(0, max(data.values) * 1.1)
            batang = ax.bar(data.index.astype(str), [0]*len(data.values), color='#e67e22')
            def anim(i):
                for idx, b in enumerate(batang):
                    b.set_height(data.values[idx] if i > idx else 0)
                return batang
            animasi = animation.FuncAnimation(fig, anim, frames=len(data.values)+1, interval=80, blit=False, repeat=False)
            ax.set_title("Pendapatan per Bulan")
        elif jenis == "Proporsi produk":
            data = sa.total_sales_per_product()
            data.plot(kind='pie', ax=ax, autopct='%1.1f%%', textprops={'color': '#333'})
            ax.set_title("Proporsi Penjualan per Produk")
        elif jenis == "Produk terlaris":
            produk, jumlah = sa.top_selling_product()
            ax.set_ylim(0, jumlah * 1.2 if jumlah > 0 else 1)
            animasi = self.animasi_grafik(fig, ax, [produk], [jumlah], kind='bar', color='orange')
            ax.set_title(f"Produk Terlaris: {produk} ({jumlah} unit)")
        elif jenis == "Rata-rata penjualan harian":
            harian = sa.data.groupby('tanggal')['jumlah_terjual'].sum().sort_index()
            rata = sa.avg_daily_sales()
            ax.set_ylim(0, max(harian.values.max(), rata) * 1.15)
            animasi = self.animasi_grafik(fig, ax, harian.index, harian.values, kind='line')
            ax.hlines(rata, harian.index.min(), harian.index.max(), colors='green', linestyle='--', label=f'Rata-rata: {rata:.2f}')
            ax.legend(loc='upper left')
            ax.set_title("Poligon Penjualan Harian")
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        ax.set_ylabel("Jumlah")
        fig.tight_layout()
        kanvas = FigureCanvasTkAgg(fig, master=self.kanvas_frame)
        kanvas.draw()
        kanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.grafik_aktif = fig
        self.animasi_aktif = animasi
        self.perbarui_statistik()
        self.isi_laporan()

    def animasi_grafik(self, fig, ax, x_data, y_data, kind='bar', color=None):
        if kind == 'bar':
            batang = ax.bar(x_data, [0]*len(y_data), color=color)
            def anim(i):
                for idx, b in enumerate(batang):
                    b.set_height(y_data[idx] if i > idx else 0)
                return batang
            return animation.FuncAnimation(fig, anim, frames=len(y_data)+1, interval=80, blit=False, repeat=False)
        elif kind == 'line':
            garis, = ax.plot([], [], marker='o', color=color or 'blue')
            def anim(i):
                garis.set_data(x_data[:i], y_data[:i])
                return garis,
            return animation.FuncAnimation(fig, anim, frames=len(x_data)+1, interval=80, blit=False, repeat=False)

    def perbarui_statistik(self):
        ringkasan = self.penganalisis_penjualan.sales_summary()
        produk, jumlah = self.penganalisis_penjualan.top_selling_product()
        self.label_tx.config(text=f"{ringkasan['transactions']}")
        self.label_unit.config(text=f"{ringkasan['units']}")
        self.label_pendapatan.config(text=f"Rp {ringkasan['income']:,}")
        self.label_produk_terlaris.config(text=f"{produk} ({jumlah} unit)")

    def isi_laporan(self):
        self.tabel_pohon.delete(*self.tabel_pohon.get_children())
        for _, baris in self.penganalisis_penjualan.data.iterrows():
            self.tabel_pohon.insert("", "end", values=(
                baris['tanggal'].strftime("%d/%m/%Y"),
                baris['produk'],
                baris['jumlah_terjual'],
                f"{baris['harga_satuan']:,}",
                f"{baris['pendapatan']:,}"
            ))

    def ekspor_csv(self):
        if not self.penganalisis_penjualan:
            messagebox.showwarning("Peringatan", "Belum ada data untuk diekspor.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if path:
            self.penganalisis_penjualan.data.to_csv(path, index=False)
            messagebox.showinfo("Sukses", f"Data berhasil disimpan ke:\n{path}")

    def ekspor_grafik(self):
        if not self.grafik_aktif:
            messagebox.showwarning("Peringatan", "Belum ada grafik untuk diekspor.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
        if path:
            self.grafik_aktif.savefig(path, dpi=150)
            messagebox.showinfo("Sukses", f"Grafik berhasil disimpan ke:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainAppGUI(root)

    teks_toggle = tk.StringVar(value="Mode Gelap")

    def ganti_tema():
        tema_saat_ini = getattr(app, 'tema_gelap', False)
        app.tema_gelap = not tema_saat_ini
        warna_bg = '#2c3e50' if app.tema_gelap else '#f0f2f5'
        panel = '#34495e' if app.tema_gelap else '#ffffff'
        teks = '#ecf0f1' if app.tema_gelap else '#333333'

        root.configure(bg=warna_bg)
        s = ttk.Style(root)
        s.configure('TFrame', background=warna_bg)
        s.configure('Paneled.TFrame', background=panel)
        s.configure('Header.TLabel', background=warna_bg, foreground=teks)
        s.configure('StatHeader.TLabel', background=panel, foreground=teks)
        s.configure('StatValue.TLabel', background=panel, foreground=teks)
        s.configure("Treeview", background=panel, fieldbackground=panel, foreground=teks)
        s.configure("Treeview.Heading", background=panel, foreground=teks)

        teks_toggle.set("Mode Terang" if app.tema_gelap else "Mode Gelap")
        app.tampilkan_analisis()

    panel_atas = ttk.Frame(root, style='TFrame')
    panel_atas.place(relx=1.0, x=-20, y=10, anchor='ne')

    tombol_toggle = ttk.Button(panel_atas, textvariable=teks_toggle, style='Accent.TButton', command=ganti_tema)

    def perbarui_tombol_toggle(*args):
        tombol_toggle.config(text=teks_toggle.get())

    teks_toggle.trace_add("write", perbarui_tombol_toggle)
    tombol_toggle.pack(ipadx=8, ipady=2)

    root.mainloop()
