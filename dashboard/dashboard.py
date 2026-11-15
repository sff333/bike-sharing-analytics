import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# Fungsi untuk memuat data secara aman (baik dijalankan dari root maupun folder dashboard)
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df['dteday'] = pd.to_datetime(df['dteday'])

    # Memastikan urutan kategori tetap konsisten
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    weather_order = ['Clear/Partly Cloudy', 'Misty/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow']
    time_order = ['Early Morning (00-04)', 'Morning Rush (05-09)', 'Midday (10-15)', 'Evening Rush (16-19)', 'Night (20-23)']
    temp_order = ['Cold (<15°C)', 'Mild (15–25°C)', 'Warm/Ideal (25–32°C)', 'Hot (>32°C)']

    df['season_label'] = pd.Categorical(df['season_label'], categories=season_order, ordered=True)
    df['weather_label'] = pd.Categorical(df['weather_label'], categories=weather_order, ordered=True)
    if 'time_cluster' in df.columns:
        df['time_cluster'] = pd.Categorical(df['time_cluster'], categories=time_order, ordered=True)
    if 'temp_cluster' in df.columns:
        df['temp_cluster'] = pd.Categorical(df['temp_cluster'], categories=temp_order, ordered=True)

    return df

hour_df = load_data()

# ================= SIDEBAR FILTER =================
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.markdown("Filter interaktif untuk mengeksplorasi performa operasional penyewaan sepeda.")

    min_date = hour_df['dteday'].min().date()
    max_date = hour_df['dteday'].max().date()

    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    season_options = ['Spring', 'Summer', 'Fall', 'Winter']
    selected_seasons = st.multiselect(
        label="Pilih Musim (Season)",
        options=season_options,
        default=season_options
    )

    weather_options = [w for w in ['Clear/Partly Cloudy', 'Misty/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow'] if w in hour_df['weather_label'].unique()]
    selected_weathers = st.multiselect(
        label="Pilih Kondisi Cuaca",
        options=weather_options,
        default=weather_options
    )

    st.markdown("---")
    st.caption("Oleh: **Shinta Feronica Florence**\nProyek Akhir Analisis Data")

# Validasi input rentang tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Memfilter DataFrame utama berdasarkan input sidebar
filtered_hour_df = hour_df[
    (hour_df['dteday'].dt.date >= start_date) &
    (hour_df['dteday'].dt.date <= end_date) &
    (hour_df['season_label'].isin(selected_seasons)) &
    (hour_df['weather_label'].isin(selected_weathers))
]

# Membuat agregasi harian dari data yang sudah difilter
filtered_day_df = filtered_hour_df.groupby('dteday', observed=False).agg(
    cnt=('cnt', 'sum'),
    registered=('registered', 'sum'),
    casual=('casual', 'sum'),
    temp_celsius=('temp_celsius', 'mean'),
    hum_percent=('hum_percent', 'mean'),
    season_label=('season_label', 'first'),
    weather_label=('weather_label', lambda x: x.mode()[0] if not x.mode().empty else None),
    temp_cluster=('temp_cluster', lambda x: x.mode()[0] if not x.mode().empty else None)
).reset_index()

# ================= HALAMAN UTAMA =================
st.title("🚲 Bike Sharing Operational & Demand Dashboard")
st.markdown(f"Menampilkan data penyewaan sepeda periode **{start_date}** hingga **{end_date}**.")

if filtered_hour_df.empty:
    st.warning("Data tidak ditemukan untuk kombinasi filter yang dipilih. Silakan sesuaikan filter di sidebar.")
    st.stop()

# 1. KPI Metrics Utama
total_rentals = int(filtered_hour_df['cnt'].sum())
total_registered = int(filtered_hour_df['registered'].sum())
total_casual = int(filtered_hour_df['casual'].sum())
avg_daily_rentals = int(filtered_day_df['cnt'].mean()) if not filtered_day_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{total_rentals:,}")
with col2:
    reg_pct = (total_registered / total_rentals * 100) if total_rentals > 0 else 0
    st.metric("Pengguna Registered", f"{total_registered:,}", f"{reg_pct:.1f}% dari total")
with col3:
    cas_pct = (total_casual / total_rentals * 100) if total_rentals > 0 else 0
    st.metric("Pengguna Casual", f"{total_casual:,}", f"{cas_pct:.1f}% dari total")
with col4:
    st.metric("Rata-Rata Harian", f"{avg_daily_rentals:,} / hari")

st.markdown("---")

# 2. Tren Penyewaan Harian
st.subheader("📈 Tren Penyewaan Sepeda Harian")
fig_trend, ax_trend = plt.subplots(figsize=(14, 4.5))
ax_trend.plot(filtered_day_df['dteday'], filtered_day_df['cnt'], color='#1f77b4', linewidth=1.5, label='Total Sewa Harian')
ax_trend.set_xlabel("Tanggal", fontsize=11)
ax_trend.set_ylabel("Jumlah Penyewaan", fontsize=11)
ax_trend.legend(loc="upper left")
sns.despine()
st.pyplot(fig_trend)

st.markdown("---")

# 3. Visualisasi Pertanyaan 1: Dampak Cuaca & Musim
st.subheader("🌤️ Pertanyaan 1: Perbandingan Penyewaan Berdasarkan Kondisi Cuaca & Musim")

col_w, col_s = st.columns(2)

with col_w:
    weather_agg = filtered_day_df.groupby('weather_label', observed=False)['cnt'].mean().dropna().reset_index()
    fig_w, ax_w = plt.subplots(figsize=(7, 5))
    if not weather_agg.empty:
        max_w = weather_agg['cnt'].max()
        w_colors = ['#1f77b4' if x == max_w else '#a6c8e0' for x in weather_agg['cnt']]
        sns.barplot(data=weather_agg, x='weather_label', y='cnt', palette=w_colors, hue='weather_label', legend=False, ax=ax_w)
        ax_w.set_title("Rata-Rata Penyewaan Harian per Kondisi Cuaca", fontsize=12, fontweight='bold')
        ax_w.set_xlabel("Kondisi Cuaca")
        ax_w.set_ylabel("Rata-Rata Penyewaan (Unit/Hari)")
        ax_w.set_ylim(0, max_w * 1.2)
        ax_w.tick_params(axis='x', rotation=12)
        for p in ax_w.patches:
            h = p.get_height()
            if pd.notna(h) and h > 0:
                ax_w.annotate(f'{h:,.0f}', (p.get_x() + p.get_width() / 2., h),
                              ha='center', va='bottom', fontsize=9.5, fontweight='bold', xytext=(0, 4), textcoords='offset points')
    sns.despine()
    st.pyplot(fig_w)

with col_s:
    season_agg = filtered_day_df.groupby('season_label', observed=False)['cnt'].mean().dropna().reset_index()
    fig_s, ax_s = plt.subplots(figsize=(7, 5))
    if not season_agg.empty:
        max_s = season_agg['cnt'].max()
        s_colors = ['#1f77b4' if x == max_s else '#a6c8e0' for x in season_agg['cnt']]
        sns.barplot(data=season_agg, x='season_label', y='cnt', palette=s_colors, hue='season_label', legend=False, ax=ax_s)
        ax_s.set_title("Rata-Rata Penyewaan Harian per Musim", fontsize=12, fontweight='bold')
        ax_s.set_xlabel("Musim (Season)")
        ax_s.set_ylabel("Rata-Rata Penyewaan (Unit/Hari)")
        ax_s.set_ylim(0, max_s * 1.2)
        for p in ax_s.patches:
            h = p.get_height()
            if pd.notna(h) and h > 0:
                ax_s.annotate(f'{h:,.0f}', (p.get_x() + p.get_width() / 2., h),
                              ha='center', va='bottom', fontsize=9.5, fontweight='bold', xytext=(0, 4), textcoords='offset points')
    sns.despine()
    st.pyplot(fig_s)

st.markdown("---")

# 4. Visualisasi Pertanyaan 2: Pola Jam Sibuk Hari Kerja vs Hari Libur
st.subheader("⏰ Pertanyaan 2: Pola Jam Operasional (Registered vs Casual) pada Hari Kerja vs Hari Libur")

working_hr = filtered_hour_df[filtered_hour_df['workingday_label'] == 'Working Day'].groupby('hr')[['registered', 'casual']].mean().reset_index()
holiday_hr = filtered_hour_df[filtered_hour_df['workingday_label'] == 'Holiday/Weekend'].groupby('hr')[['registered', 'casual']].mean().reset_index()

fig_hr, axes_hr = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)

# Subplot Hari Kerja
if not working_hr.empty:
    axes_hr[0].plot(working_hr['hr'], working_hr['registered'], marker='o', linewidth=2.2, color='#1f77b4', label='Registered')
    axes_hr[0].plot(working_hr['hr'], working_hr['casual'], marker='s', linewidth=2.2, color='#ff7f0e', label='Casual')
axes_hr[0].set_title("Hari Kerja (Working Day)", fontsize=12, fontweight='bold')
axes_hr[0].set_xlabel("Jam Operasional (00:00 - 23:00)")
axes_hr[0].set_ylabel("Rata-Rata Penyewaan / Jam")
axes_hr[0].set_xticks(range(0, 24, 2))
axes_hr[0].legend()

# Subplot Hari Libur
if not holiday_hr.empty:
    axes_hr[1].plot(holiday_hr['hr'], holiday_hr['registered'], marker='o', linewidth=2.2, color='#1f77b4', label='Registered')
    axes_hr[1].plot(holiday_hr['hr'], holiday_hr['casual'], marker='s', linewidth=2.2, color='#ff7f0e', label='Casual')
axes_hr[1].set_title("Hari Libur / Akhir Pekan (Holiday/Weekend)", fontsize=12, fontweight='bold')
axes_hr[1].set_xlabel("Jam Operasional (00:00 - 23:00)")
axes_hr[1].set_xticks(range(0, 24, 2))
axes_hr[1].legend()

sns.despine()
plt.tight_layout()
st.pyplot(fig_hr)

st.markdown("---")

# 5. Visualisasi Analisis Lanjutan: Clustering (Manual Grouping & Binning)
st.subheader("🔍 Analisis Lanjutan: Klaster Waktu Operasional & Klaster Kenyamanan Suhu")

col_tc, col_temp = st.columns(2)

with col_tc:
    tc_agg = filtered_hour_df.groupby('time_cluster', observed=False)['cnt'].mean().dropna().reset_index()
    fig_tc, ax_tc = plt.subplots(figsize=(7, 5))
    if not tc_agg.empty:
        max_tc = tc_agg['cnt'].max()
        tc_colors = ['#1f77b4' if x == max_tc else '#a6c8e0' for x in tc_agg['cnt']]
        sns.barplot(data=tc_agg, x='time_cluster', y='cnt', palette=tc_colors, hue='time_cluster', legend=False, ax=ax_tc)
        ax_tc.set_title("Rata-Rata Sewa per Jam Berdasarkan Klaster Waktu", fontsize=12, fontweight='bold')
        ax_tc.set_xlabel("Klaster Waktu (Manual Grouping)")
        ax_tc.set_ylabel("Rata-Rata Penyewaan (Unit/Jam)")
        ax_tc.set_ylim(0, max_tc * 1.2)
        ax_tc.tick_params(axis='x', rotation=15)
        for p in ax_tc.patches:
            h = p.get_height()
            if pd.notna(h) and h > 0:
                ax_tc.annotate(f'{h:,.1f}', (p.get_x() + p.get_width() / 2., h),
                               ha='center', va='bottom', fontsize=9.5, fontweight='bold', xytext=(0, 4), textcoords='offset points')
    sns.despine()
    st.pyplot(fig_tc)

with col_temp:
    temp_agg = filtered_day_df.groupby('temp_cluster', observed=False)['cnt'].mean().dropna().reset_index()
    fig_temp, ax_temp = plt.subplots(figsize=(7, 5))
    if not temp_agg.empty:
        max_temp = temp_agg['cnt'].max()
        t_colors = ['#1f77b4' if x == max_temp else '#a6c8e0' for x in temp_agg['cnt']]
        sns.barplot(data=temp_agg, x='temp_cluster', y='cnt', palette=t_colors, hue='temp_cluster', legend=False, ax=ax_temp)
        ax_temp.set_title("Rata-Rata Sewa Harian Berdasarkan Klaster Suhu", fontsize=12, fontweight='bold')
        ax_temp.set_xlabel("Kategori Suhu Udara (Binning)")
        ax_temp.set_ylabel("Rata-Rata Penyewaan (Unit/Hari)")
        ax_temp.set_ylim(0, max_temp * 1.2)
        ax_temp.tick_params(axis='x', rotation=12)
        for p in ax_temp.patches:
            h = p.get_height()
            if pd.notna(h) and h > 0:
                ax_temp.annotate(f'{h:,.0f}', (p.get_x() + p.get_width() / 2., h),
                                 ha='center', va='bottom', fontsize=9.5, fontweight='bold', xytext=(0, 4), textcoords='offset points')
    sns.despine()
    st.pyplot(fig_temp)

st.caption("Copyright © 2026 Shinta Feronica Florence | Bike Sharing Dataset Dashboard")