import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Poope & Pee",
    page_icon="💩",
    layout="wide",
)

key = '1GfLQYA0g04Rjib0xMtOzwGA_vnJP0NSGuZLENI71EgI'


# @st.cache_data
def get_data() -> pd.DataFrame:
    df = pd.read_csv('https://docs.google.com/spreadsheets/d/' +
                     key +
                     '/export?gid=0&format=csv',
                     parse_dates=['Date'],
                     dayfirst=True)

    return df


df = get_data()
types = ['All'] + df['Type'].dropna().unique().tolist()

st.title("Poope & Pee")
filter_ = st.selectbox("Select type:", types)

placeholder = st.empty()

while True:
    df = get_data()

    real_types = df['Type'].dropna().unique().tolist()
    date = pd.Timestamp.now()

    with placeholder.container():
        kpi_list = st.columns(len(real_types) * 2)

        for i, kpi in enumerate(kpi_list[:len(real_types)]):
            kpi.metric(
                label=f"{real_types[i]}s count",
                value=len(df[df['Type'] == real_types[i]]),
                delta=len(df[:-1][df['Type'] == real_types[i]]),
            )

        for i, kpi in enumerate(kpi_list[len(real_types):]):
            kpi.metric(
                label=f"Minutes from last {real_types[i]}",
                value=int((date - df[df['Type'] == real_types[i]]['Date'].values[-1]) / np.timedelta64(1, 'm')),
            )

        st.markdown(f"### {filter_}s by date")
        cur_df = df if filter_ == 'All' else df[df['Type'] == filter_]
        fig = px.line(
            data_frame=cur_df, y='Type', x='Date'
        )
        st.write(fig)

        st.markdown("### Full Table")
        st.dataframe(df)

    time.sleep(30)
