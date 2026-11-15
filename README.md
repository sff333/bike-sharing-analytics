# Bike Sharing Analytics Dashboard 🚲✨

Proyek akhir analisis data menggunakan **Bike Sharing Dataset** (2011–2012) untuk mengeksplorasi dampak kondisi cuaca, pergantian musim, pola jam sibuk operasional (*Working Day* vs *Holiday/Weekend*), serta pengelompokan klaster waktu dan suhu (*Manual Grouping & Binning*).

## Struktur Direktori
```text
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard/dashboard.py
```

**2. Pastikan Versi Library di `requirements.txt` Aman untuk Streamlit Cloud**
Pastikan isi `requirements.txt` bersih seperti ini (tanpa `env` lokal yang mengunci versi khusus Windows agar tidak gagal saat di-deploy ke server Linux Streamlit Cloud):

```text
pandas
numpy
matplotlib
seaborn
streamlit
