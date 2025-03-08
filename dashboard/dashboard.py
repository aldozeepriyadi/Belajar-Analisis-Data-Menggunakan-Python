import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import numpy as np

# Fungsi untuk memuat data
def load_data():
    return pd.read_csv('dashboard/hour_data.csv')

# Membaca data
hour_df = load_data()

# Mengubah kolom 'dteday' menjadi format tanggal
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Sidebar untuk pilihan navigasi menggunakan tombol
st.sidebar.title('Dashboard Penyewaan Sepeda')
home_button = st.sidebar.button("🏠 Home")
informasi_button = st.sidebar.button("📊 Informasi Dataset")
analisis_lanjutan_button = st.sidebar.button("🔍 Analisis Lanjutan")

# Filter berdasarkan tanggal
st.sidebar.subheader('Filter data')
start_date = st.sidebar.date_input("Tanggal Awal", hour_df['dteday'].min())
end_date = st.sidebar.date_input("Tanggal Akhir", hour_df['dteday'].max())

# Menyimpan filter tanggal ke dalam session_state agar tidak hilang saat halaman di-refresh
if 'start_date' not in st.session_state:
    st.session_state.start_date = start_date
if 'end_date' not in st.session_state:
    st.session_state.end_date = end_date

# Menyimpan halaman yang aktif di session_state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Menyimpan nilai tanggal terbaru yang dipilih
if start_date != st.session_state.start_date:
    st.session_state.start_date = start_date

if end_date != st.session_state.end_date:
    st.session_state.end_date = end_date

# Filter data berdasarkan rentang tanggal yang dipilih
filtered_df = hour_df[(hour_df['dteday'] >= pd.to_datetime(st.session_state.start_date)) & 
                       (hour_df['dteday'] <= pd.to_datetime(st.session_state.end_date))]

# Menentukan halaman yang aktif berdasarkan tombol yang diklik
if home_button:
    st.session_state.page = "Home"
elif informasi_button:
    st.session_state.page = "Informasi Dataset"
elif analisis_lanjutan_button:
    st.session_state.page = "Analisis Lanjutan"

# Home Page
if st.session_state.page == "Home":
    st.title('Dashboard Penyewaan Sepeda')
    st.write("""
        Dashboard ini menganalisis dataset tentang penyewaan sepeda berdasarkan berbagai faktor seperti 
        musim, cuaca, waktu dalam sehari, serta jenis penyewa (biasa dan terdaftar). Gunakan menu navigasi di sidebar
        untuk memilih analisis yang ingin dilihat.
    """)
    st.write(f"Menampilkan data dari {st.session_state.start_date} hingga {st.session_state.end_date}.")

    # Analisis 1: Pengaruh Musim dan Cuaca
    st.subheader('Pertanyaan 1: Bagaimana kondisi musim mempengaruhi jumlah penyewaan sepeda?')

    # Definisikan season_mapping di sini sebelum digunakan
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    filtered_df['season_name'] = filtered_df['season'].map(season_mapping)

    # Scatter Plot: Suhu vs Jumlah Penyewaan Sepeda
    st.subheader('Jumlah Penyewaan Sepeda berdasarkan Suhu')
    fig, ax = plt.subplots(figsize=(10, 6))  # Membuat figure dan axes terlebih dahulu
    ax.scatter(filtered_df['temp'], filtered_df['cnt'], alpha=0.5, color='b', marker='o')
    ax.set_title('Jumlah Penyewaan Sepeda berdasarkan Suhu')
    ax.set_xlabel('Suhu')
    ax.set_ylabel('Jumlah Penyewa')
    ax.grid(True)
    st.pyplot(fig)  # Menggunakan figure yang sudah didefinisikan

    # Scatter Plot: Kecepatan Angin vs Jumlah Penyewaan Sepeda
    st.subheader('Jumlah Penyewaan Sepeda berdasarkan Kecepatan Angin')
    fig, ax = plt.subplots(figsize=(10, 6))  # Membuat figure dan axes terlebih dahulu
    ax.scatter(filtered_df['windspeed'], filtered_df['cnt'], alpha=0.5, color='r', marker='o')
    ax.set_title('Jumlah Penyewaan Sepeda berdasarkan Kecepatan Angin')
    ax.set_xlabel('Kecepatan Angin')
    ax.set_ylabel('Jumlah Penyewa')
    ax.grid(True)
    st.pyplot(fig)  # Menggunakan figure yang sudah didefinisikan

    # Barplot: Jumlah Penyewaan Sepeda per Musim
    st.subheader('Jumlah Penyewaan Sepeda berdasarkan Musim')
    season_grouped = filtered_df.groupby(by="season_name").agg(
        instant_nunique=('instant', 'nunique'),
        cnt_sum=('cnt', 'sum'),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))  # Membuat figure dan axes terlebih dahulu
    sns.barplot(x='season_name', y='cnt_sum', data=season_grouped, ax=ax)
    ax.set_title('Jumlah Penyewaan Sepeda per Musim')
    ax.set_xlabel('Season')
    ax.set_ylabel('Jumlah Penyewaan Sepeda')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x / 1e5):,}K'))
    st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.write(""" 
            Dari grafik hubungan antara suhu dan jumlah penyewaan sepeda, terlihat bahwa semakin tinggi suhu (semakin hangat), semakin banyak jumlah penyewaan sepeda. Ini menunjukkan bahwa suhu yang lebih hangat meningkatkan minat masyarakat untuk menyewa sepeda.
            Sebaliknya, hubungan antara kecepatan angin dan jumlah penyewaan sepeda menunjukkan korelasi negatif. Ketika kecepatan angin meningkat, jumlah penyewaan sepeda cenderung menurun. Ini menunjukkan bahwa kondisi berangin dapat mengurangi kenyamanan bersepeda, sehingga orang cenderung menghindari bersepeda saat angin kencang.
            Musim panas (Summer) memiliki jumlah penyewaan sepeda tertinggi, mencerminkan pengaruh suhu hangat pada meningkatnya minat bersepeda.
            Musim gugur (Fall) juga menunjukkan jumlah penyewaan sepeda yang cukup tinggi, meskipun tidak setinggi musim panas. Mungkin karena suhu yang lebih moderat dan nyaman.
        """)

    # Analisis 2: Penyewaan Sepeda per Jam
    st.subheader('Pertanyaan 2: Di jam-jam tertentu pada hari kerja, apakah jumlah penyewaan sepeda rata-rata lebih dari 3000 sepeda dalam satu jam?')
    # Penyewaan sepeda per jam
    workingdays = filtered_df[(filtered_df['workingday'] == 1)]
    hourly = workingdays.groupby('hr').agg({"cnt": "sum"})

    workingdays_holiday = filtered_df[(filtered_df['workingday'] == 0)]
    hourly_holiday = workingdays_holiday.groupby('hr').agg({"cnt": "sum"})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))  # Membuat figure dan axes terlebih dahulu

    ax1.plot(hourly.index, hourly['cnt'], color='skyblue', marker='o', label='Penyewaan Sepeda')
    ax1.axhline(3000, color='red', linestyle='--', label='3000 Penyewaan Sepeda')
    ax1.set_title('Jumlah Penyewaan Sepeda per Jam Pada Hari Kerja', fontsize=14)
    ax1.set_xlabel('Jam', fontsize=12)
    ax1.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    ax1.legend()

    ax2.plot(hourly_holiday.index, hourly_holiday['cnt'], color='skyblue', marker='o', label='Penyewaan Sepeda')
    ax2.axhline(3000, color='red', linestyle='--', label='3000 Penyewaan Sepeda')
    ax2.set_title('Jumlah Penyewaan Sepeda per Jam Pada Hari Libur', fontsize=14)
    ax2.set_xlabel('Jam', fontsize=12)
    ax2.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    ax2.legend()

    plt.tight_layout()
    st.pyplot(fig)  # Menggunakan figure yang sudah didefinisikan

    with st.expander("Penjelasan"):
        st.write(""" 
            Pada grafik pertama, yang menunjukkan jumlah penyewaan sepeda per jam pada hari kerja, Banyak jam yang mencapai atau melebihi 3000 penyewaan sepeda dalam satu jam. Meskipun ada beberapa fluktuasi, grafik ini menunjukkan bahwa jumlah penyewaan sepeda tiap jam melampaui angka 3000 terutama pada saat jam-jam berangkat dan pulang kerja yang mencapai puncak yaitu jam 07:00 hingga 09:00 dan jam 16:00 hingga 18:00.
            Pada grafik kedua, yang menunjukkan jumlah penyewaan sepeda per jam pada hari libur, terlihat bahwa ada jam-jam tertentu di mana jumlah penyewaan sepeda melebihi 3000. Puncak tertinggi terjadi pada sekitar jam 14:00 hingga 16:00.
            Grafik ini menunjukkan adanya lonjakan signifikan pada hari kerja yang terlihat dari jumlahnya, di mana penyewaan sepeda lebih banyak dibandingkan dengan hari libur.
        """)

    # Analisis 3: Penyewa Biasa vs Terdaftar
    st.subheader('Pertanyaan 3: Bagaimana kondisi antara penyewa biasa dan penyewa terdaftar memengaruhi jumlah total penyewaan sepeda?')
    member_casual = filtered_df.groupby("weekday")[["casual"]].sum()
    member_registered = filtered_df.groupby("weekday")[["registered"]].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))  # Membuat figure dan axes terlebih dahulu

    ax1.bar(member_casual.index, member_casual['casual'], color='skyblue', label='Penyewa Biasa')
    ax1.set_title('Jumlah Penyewaan Sepeda oleh Penyewa Biasa per Hari', fontsize=14)
    ax1.set_xlabel('Hari', fontsize=12)
    ax1.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    ax1.set_xticks(range(7))
    ax1.set_xticklabels(['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'], fontsize=10)
    ax1.legend()

    ax2.bar(member_registered.index, member_registered['registered'], color='orange', label='Penyewa Terdaftar')
    ax2.set_title('Jumlah Penyewaan Sepeda oleh Penyewa Terdaftar per Hari', fontsize=14)
    ax2.set_xlabel('Hari', fontsize=12)
    ax2.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    ax2.set_xticks(range(7))
    ax2.set_xticklabels(['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'], fontsize=10)
    ax2.legend()

    plt.tight_layout()
    st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.write(""" 
            Pada Grafik Penyewa Terdaftar (registered) menunjukkan bahwa penyewa terdaftar memiliki jumlah penyewaan sepeda yang lebih konsisten dan lebih tinggi sepanjang minggu. Secara keseluruhan, penyewa terdaftar berkontribusi lebih besar pada total penyewaan sepeda setiap hari, dengan puncak pada Jumat dan Sabtu.
            Pada Grafik Penyewa biasa (casual) menunjukkan fluktuasi yang lebih besar. Jumlah penyewaan sepeda oleh penyewa biasa lebih rendah dibandingkan penyewa terdaftar, dengan puncak tinggi pada Minggu. Hal ini menunjukkan bahwa penyewa biasa cenderung lebih banyak pada akhir pekan, khususnya di hari Minggu, sementara pada hari kerja jumlahnya relatif lebih rendah.
            Penyewa terdaftar lebih banyak dan lebih stabil dalam menyewa sepeda sepanjang minggu, sedangkan penyewa biasa lebih banyak pada akhir pekan (terutama Minggu). Penyewa terdaftar memainkan peran yang lebih besar dalam total penyewaan sepeda secara keseluruhan, terutama pada hari-hari kerja dan sebagian besar akhir pekan.
        """)

# Informasi Dataset Page
elif st.session_state.page == "Informasi Dataset":
    st.title("Informasi Dataset")
    st.write(""" 
        Dataset ini berasal dari sistem berbagi sepeda Capital Bikeshare di Washington D.C., USA, dan mencatat dua tahun log historis 
        dari tahun 2011 dan 2012. Data ini tersedia secara publik di [situs Capital Bikeshare](http://capitalbikeshare.com/system-data) 
        dan mengandung informasi terkait penggunaan sepeda serta kondisi cuaca dan musim.
    """)
    
    st.write(""" 
        ### Sumber Data
        - Data dikumpulkan dari sistem berbagi sepeda Capital Bikeshare yang mencatat aktivitas penyewaan sepeda per jam dan per hari.
        - Data cuaca diambil dari [Freemeteo](http://www.freemeteo.com).
        
        ### Karakteristik Data
        - **Tanggal dan Waktu**: Data yang tersedia mencatat waktu penyewaan sepeda, yang disusun dalam interval dua jam dan harian.
        - **Kondisi Cuaca**: Termasuk informasi suhu, kecepatan angin, kelembapan, dan presipitasi, yang dapat memengaruhi perilaku penyewaan sepeda.
        - **Informasi Musim**: Musim dan kondisi lingkungan, yang juga sangat memengaruhi pola sewa sepeda (misalnya, lebih banyak orang menyewa sepeda di musim panas).
        
        ### Faktor yang Mempengaruhi Penyewaan Sepeda
        - **Cuaca**: Kondisi cuaca seperti hujan atau panas dapat memengaruhi jumlah penyewaan sepeda.
        - **Hari dalam Minggu**: Ada pola penyewaan yang berbeda pada hari kerja dibandingkan hari libur.
        - **Musim**: Musim seperti musim panas atau musim dingin dapat berdampak pada jumlah penyewaan sepeda.
        - **Waktu dalam Sehari**: Penyewaan sepeda juga bervariasi tergantung pada waktu (pagi, siang, malam).
        
        ### Tujuan Dataset
        Dataset ini menyediakan informasi penting yang dapat digunakan untuk analisis tentang bagaimana berbagai faktor eksternal 
        memengaruhi penyewaan sepeda di kota besar. Selain itu, dataset ini juga memungkinkan untuk analisis mobilitas dan 
        perencanaan transportasi berbasis data untuk kota-kota besar, yang dapat memberikan wawasan berharga dalam meningkatkan 
        efisiensi sistem transportasi dan memperbaiki kualitas hidup kota.
    """)
    st.write("Lihat beberapa baris pertama dari dataset: ")
    st.write(filtered_df.head())

# Analisis Lanjutan
elif st.session_state.page == 'Analisis Lanjutan':
    st.title('Analisis Lanjutan (Manual Grouping)')
    st.subheader('Proporsi Penyewaan Sepeda per Waktu dalam Sehari Berdasarkan Pengelompokan Waktu (Pagi, Siang, Malam)')

    def manual_grouping(hour):
        if 6 <= hour < 12:
            return 'Pagi'
        elif 12 <= hour < 18:
            return 'Siang'
        else:
            return 'Malam'

    filtered_df['Time_of_Day'] = filtered_df['hr'].apply(manual_grouping)
    manual_grouping_data = filtered_df.groupby('Time_of_Day')[['cnt']].sum()

    # Pie chart untuk proporsi penyewaan sepeda
    fig, ax = plt.subplots(figsize=(8, 8))  # Membuat figure dan axes terlebih dahulu
    manual_grouping_data['cnt'].plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['skyblue', 'orange', 'green'], ax=ax, legend=False)

    ax.set_title('Proporsi Penyewaan Sepeda per Waktu dalam Sehari (Pagi, Siang, Malam)', fontsize=14)
    ax.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)  # Update y-label untuk lebih informatif
    plt.tight_layout()
    st.pyplot(fig)
    with st.expander("Penjelasan Analisis Lanjutan"):
        st.write(""" 
            **Analisis Lanjutan (Manual Grouping)**

            Waktu siang menunjukkan jumlah penyewaan sepeda yang paling tinggi, yang bisa menunjukkan bahwa banyak orang menyewa sepeda untuk kegiatan sehari-hari.
            Meskipun malam hari sedikit lebih tinggi dari pagi, kedua waktu tersebut menunjukkan angka penyewaan yang lebih rendah dibandingkan dengan siang hari.
        """)
