# Dashboard Analisis E-Commerce Olist

Dashboard interaktif berbasis Streamlit untuk proyek analisis data **E-Commerce Public Dataset (Olist, Brazil)**. Dashboard ini menjawab tiga pertanyaan bisnis dari notebook analisis, ditambah segmentasi pelanggan dengan RFM.

## Pertanyaan Bisnis

1. Kategori produk apa saja yang memiliki revenue terbesar (10 teratas) dari pesanan delivered sepanjang 2017, dan berapa kontribusinya terhadap total revenue?
2. Berapa selisih rata-rata review score antara pesanan tepat waktu dan terlambat? State mana yang memiliki persentase keterlambatan tertinggi pada periode Januari 2017 - Agustus 2018?
3. Bulan apa yang memiliki jumlah order dan revenue tertinggi, serta bagaimana pertumbuhan revenue Month-over-Month (MoM) pada periode Januari 2017 - Agustus 2018?

## Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv
│   ├───order_data.csv
│   ├───rfm_data.csv
│   └───dashboard.py
├───data
│   └───(dataset E-Commerce Public Dataset)
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment

Pastikan Python 3.9 atau lebih baru sudah terpasang.

### Menggunakan virtual environment (disarankan)

```
cd submission
python -m venv venv
```

Aktifkan environment:

- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Pasang library yang dibutuhkan:

```
pip install -r requirements.txt
```

### Menggunakan Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Menjalankan Dashboard

Dari folder `submission`:

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka otomatis di `http://localhost:8501`. Jika tidak terbuka, salin alamat tersebut ke browser. Tekan `Ctrl + C` di terminal untuk menghentikannya.

Jika perintah `streamlit` tidak dikenali, gunakan:

```
python -m streamlit run dashboard/dashboard.py
```

## Catatan

- Berkas `main_data.csv`, `order_data.csv`, dan `rfm_data.csv` dihasilkan oleh `notebook.ipynb` dan harus berada satu folder dengan `dashboard.py`.
- Analisis hanya memakai pesanan berstatus `delivered`. Revenue dihitung dari harga item tanpa ongkos kirim.
- Analisis lanjutan yang digunakan adalah RFM dengan pengelompokan manual (grouping dan binning), tanpa algoritma machine learning.

## Isi Dashboard

| Tab | Isi |
|---|---|
| Kategori Produk | Revenue per kategori pada 2017 dan konsentrasi revenue |
| Pengiriman dan Review | Review score berdasarkan keterlambatan dan state dengan keterlambatan tertinggi |
| Tren Penjualan | Order dan revenue bulanan, pertumbuhan MoM, serta pola order per hari dan jam |
| Segmentasi Pelanggan | Segmen pelanggan hasil analisis RFM |
| Kesimpulan | Ringkasan jawaban dan rekomendasi |

## Sumber Data

Brazilian E-Commerce Public Dataset by Olist.
