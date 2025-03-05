import streamlit as st
import pandas as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt


def load_and_process_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'main_data.csv')
    df = pd.read_csv(csv_file_path)
    df['dteday_x'] = pd.to_datetime(df['dteday_x'])
    

    last_rent_date = df['dteday_x'].max()
    df['recency'] = (last_rent_date - df['dteday_x']).dt.days
    df['frequency'] = df.groupby('cnt_x')['cnt_x'].transform('count')
    df['monetary'] = df['cnt_x']
    

    quantiles = df[['recency', 'frequency', 'monetary']].quantile([0.25, 0.5, 0.75])


    def rfm_score(x, quantiles):
        if x <= quantiles[0.25]:
            return 1
        elif x <= quantiles[0.5]:
            return 2
        elif x <= quantiles[0.75]:
            return 3
        else:
            return 4
    
    df['recency_score'] = df['recency'].apply(rfm_score, quantiles=quantiles['recency'])
    df['frequency_score'] = df['frequency'].apply(rfm_score, quantiles=quantiles['frequency'])
    df['monetary_score'] = df['monetary'].apply(rfm_score, quantiles=quantiles['monetary'])

    df['rfm_group'] = df['recency_score'].astype(str) + df['frequency_score'].astype(str) + df['monetary_score'].astype(str)

 
    bins = [0, 1000, 2000, 3000, 4000, 5000]
    labels = ['Low', 'Medium', 'High', 'Very High', 'Extreme']
    df['rental_group'] = pd.cut(df['cnt_x'], bins=bins, labels=labels)

    bin_edges = [0,1000, 2000, 3000, 4000, 5000]
    bin_labels = ['0-1000', '1001-2000', '2001-3000', '3001-4000', '4001-5000']
    df['cnt_group'] = pd.cut(df['cnt_x'], bins=bin_edges, labels=bin_labels)

    return df


def create_season_grouped_df(df):
    season_grouped_avg = df.groupby(by="season_x").agg(
        instant_nunique=('instant', 'nunique'),
        cnt_max=('cnt_x', 'max'),
        cnt_min=('cnt_x', 'min'),
        cnt_mean=('cnt_x', 'mean'),
        cnt_std=('cnt_x', 'std')
    ).reset_index()

    season_mapping = {
        1: 'Musim Semi',
        2: 'Musim Panas',
        3: 'Musim Gugur',
        4: 'Musim Dingin'
    }

    season_grouped_avg['season_name'] = season_grouped_avg['season_x'].map(season_mapping)
    season_grouped_avg = season_grouped_avg[['season_name', 'instant_nunique', 'cnt_max', 'cnt_min', 'cnt_mean', 'cnt_std']]
    return season_grouped_avg


st.title('Dashboard Penyewaan Sepeda')

df = load_and_process_data()


with st.sidebar:
    
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

analysis_option = st.sidebar.selectbox(
    'Pilih Analisis',
    ['Analisis Musim', 'Analisis Kondisi Cuaca', 'Analisis Jam Puncak Penyewaan', 'Analisis RFM', 'Clustering Penyewaan']
)
st.sidebar.header('Filter berdasarkan Tanggal')
start_date = st.sidebar.date_input('Tanggal Mulai', df['dteday_x'].min())
end_date = st.sidebar.date_input('Tanggal Selesai', df['dteday_x'].max())


filtered_df = df[(df['dteday_x'] >= pd.to_datetime(start_date)) & (df['dteday_x'] <= pd.to_datetime(end_date))]




st.write(f"Data dari {start_date} hingga {end_date}")
st.dataframe(filtered_df)


if analysis_option == 'Analisis Musim':
    season_grouped_avg = create_season_grouped_df(filtered_df)
    st.header("1. Bagaimana Musim Mempengaruhi Penyewaan Sepeda?")
    st.write("""Bagian ini menunjukkan pengaruh musim terhadap jumlah penyewaan sepeda.""")

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='season_name', y='cnt_mean', data=season_grouped_avg, ax=ax1)
    ax1.set_title('Rata-rata Penyewaan Sepeda per Musim')
    ax1.set_xlabel('Musim')
    ax1.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig1)

elif analysis_option == 'Analisis Kondisi Cuaca':
    st.header("2. Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
    st.write("""Bagian ini menunjukkan bagaimana kondisi cuaca mempengaruhi jumlah penyewaan sepeda.""")


    weather_type_df = filtered_df[filtered_df['weathersit_x'].isin([1, 2, 3, 4])]

    weather_type_df['weather_condition'] = weather_type_df['weathersit_x'].apply(
        lambda x: 'Normal' if x in [1, 2] else 'Extreme'
    )
    

    weather_condition_grouped = weather_type_df.groupby('weather_condition').agg({
        "cnt_x": ["mean", "std", "max", "min"]
    }).reset_index()


    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weather_condition', y=('cnt_x', 'mean'), data=weather_condition_grouped, ax=ax2)
    ax2.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca')
    ax2.set_xlabel('Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig2)

elif analysis_option == 'Analisis Jam Puncak Penyewaan':
    st.header("3. Penyewaan Sepeda pada Jam Puncak")
    st.write("""Bagian ini menganalisis apakah jumlah penyewaan sepeda lebih dari 3000 pada jam-jam tertentu.""")

    peak_hours = filtered_df.groupby('hr').agg({"cnt_x": "mean"}).reset_index()
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='hr', y='cnt_x', data=peak_hours, color='skyblue', ax=ax4)
    ax4.axhline(3000, color='red', linestyle='--', label='3000 Penyewaan')
    ax4.set_title('Rata-rata Penyewaan Sepeda per Jam')
    ax4.set_xlabel('Jam')
    ax4.set_ylabel('Rata-rata Penyewaan Sepeda')
    ax4.legend()
    st.pyplot(fig4)

elif analysis_option == 'Analisis RFM':
    st.header("4. Analisis RFM Penyewaan Sepeda")
    st.write("""Bagian ini menunjukkan bagaimana recency, frequency, dan monetary mempengaruhi pola penyewaan sepeda.""")

    rfm_data = filtered_df[['recency', 'frequency', 'monetary']]
    correlation_matrix = rfm_data.corr()

    fig5, ax5 = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", cbar=True, ax=ax5)
    ax5.set_title('Korelasi Antar Parameter RFM Berdasarkan Perilaku Penyewa')
    st.pyplot(fig5)

elif analysis_option == 'Clustering Penyewaan':
    st.header("5. Clustering Penyewaan Sepeda")
    st.write("""Bagian ini menunjukkan distribusi pelanggan berdasarkan grup penyewaan.""")

    fig6, ax6 = plt.subplots(figsize=(8, 6))
    sns.countplot(x='rental_group', data=filtered_df, hue='rental_group', palette='Set2', ax=ax6)
    ax6.set_title('Distribusi Pelanggan Berdasarkan Grup Penyewaan')
    ax6.set_xlabel('Grup Penyewaan')
    ax6.set_ylabel('Jumlah Pelanggan')
    st.pyplot(fig6)

    st.write("""Bagian ini menunjukkan distribusi pelanggan berdasarkan grup penyewaan.""")
