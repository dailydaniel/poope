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
filter_type = st.selectbox("Select type:", types)
filter_period = st.selectbox("Select period:", ['Month', 'Week', 'Day'])
filter2gb = {'Month': 'M', 'Week': 'W-MON', 'Day': 'D'}[filter_period]

placeholder = st.empty()

while True:
    df = get_data()

    real_types = df['Type'].dropna().unique().tolist()
    date = pd.Timestamp.now()

    with placeholder.container():
        kpi_list = st.columns(len(real_types) * 2)

        for i, kpi in enumerate(kpi_list[:len(real_types)]):
            val = len(df[df['Type'] == real_types[i]])
            d = val - len(df[:-1][df['Type'] == real_types[i]])
            kpi.metric(label=f"{real_types[i]}s count", value=val, delta=d)

        for i, kpi in enumerate(kpi_list[len(real_types):]):
            kpi.metric(
                label=f"Minutes from last {real_types[i]}",
                value=int((date - df[df['Type'] == real_types[i]]['Date'].values[-1]) / np.timedelta64(1, 'm')) + 180,
            )

        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.markdown(f"<h4 style='text-align: center;'>{filter_type}s by date</h4>", unsafe_allow_html=True)
            df_vis = df if filter_type == 'All' else df[df['Type'] == filter_type]
            fig1 = px.line(data_frame=df_vis, y='Type', x='Date', hover_data=['Info'])
            st.write(fig1)

        with fig_col2:
            st.markdown(f"<h4 style='text-align: center;'>Bars by {filter_period}s</h1>", unsafe_allow_html=True)
            st.dataframe(df)
            # df_gb = df.groupby(pd.Grouper(key='Date', freq='D'),
            #                    as_index=False)['Type'].value_counts()
            # fig2 = px.bar(data_frame=df_gb, y='count', x='Date', color='Type')
            # st.write(fig2)

        st.markdown("### Full Table")
        st.dataframe(df)

    time.sleep(60)
