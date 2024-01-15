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
st.markdown("Start: 2024-01-14. Logbook of my pee and poope.")
st.markdown("Powered by google sheet and siri shortcuts.")
st.markdown("Version 2.1")
url_tg = "https://t.me/mandanya77"
st.markdown("made by Daniel Zholkovsky [telegram](%s)" % url_tg)
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
                label=f"Hours from last {real_types[i]}",
                value=int((date - df[df['Type'] == real_types[i]]['Date'].values[-1]) / np.timedelta64(1, 'h')) + 3,
            )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<h4 style='text-align: center;'>{filter_type} distribution per Day</h4>", unsafe_allow_html=True)
            dt = 100 / df.index.size + 2
            df_vis = df if filter_type == 'All' else df[df['Type'] == filter_type]
            df_vis['Y'] = np.random.random(df_vis.index.size) / dt + 0.5
            df_vis['X'] = df_vis['Date'].dt.time
            df_vis = df_vis.sort_values('X')
            fig1 = px.scatter(data_frame=df_vis, y='Y', x='X', color='Type')
            fig1.update_layout(legend=dict(yanchor="top", y=1.2, xanchor="left", x=0.01))
            fig1.update_layout(
                # autosize=False,
                # width=750,
                # height=500,
                margin=dict(
                    l=50,
                    r=500,
                    # b=50,
                    # t=50,
                    # pad=4
                ),
            )

            st.write(fig1)

        with col2:
            st.markdown(f"<h4 style='text-align: center;'>Bar chart by {filter_period}</h1>", unsafe_allow_html=True)
            df_gb = df.groupby(pd.Grouper(key='Date', freq=filter2gb))['Type'].value_counts().reset_index()
            fig2 = px.bar(data_frame=df_gb, y='count', x='Date', color='Type')
            fig2.update_layout(legend=dict(yanchor="top", y=1.2, xanchor="left", x=0.01))
            fig1.update_layout(
                # autosize=False,
                # width=750,
                # height=500,
                margin=dict(
                    l=50,
                    r=50,
                    # b=50,
                    # t=50,
                    # pad=4
                ),
            )
            st.write(fig2)

        st.markdown("### Full Table")
        st.dataframe(df)

    time.sleep(60)
