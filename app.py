import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib
from random import choices
import requests

import warnings
warnings.simplefilter('ignore')


st.set_page_config(
    page_title="Poope & Pee",
    page_icon="💩",
    layout="wide",
)

key = '1GfLQYA0g04Rjib0xMtOzwGA_vnJP0NSGuZLENI71EgI'
url_base = "https://push.techulus.com/api/v1/notify/08b75608-8570-470d-987b-a507529cf525/?title="
url_end = "&body={}"


def get_d(n: int, delta: int = 0.01):
    res = []

    if n % 2 != 0:
        res.append(0)
        n -= 1

    for i in range(n):
        if i % 2 == 0:
            res.append(delta + delta * (i // 2))
        else:
            res.append(-delta - delta * (i // 2))

    return pd.Series(res).sample(len(res)).values


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
colors = dict(matplotlib.colors.cnames.items())
hex_colors = tuple(colors.values())

st.title("Poope & Pee")
st.markdown("Start: 2024-01-14. Logbook of my pee and poope.")
st.markdown("Powered by google sheet and siri shortcuts.")
url_tg = "https://t.me/mandanya77"
st.markdown("made by Daniel Zholkovsky [telegram](%s)" % url_tg)
st.markdown("Version 2.12")
filter_type = st.selectbox("Select type:", types)
filter_period = st.selectbox("Select period:", ['Day', 'Week', 'Month'])
filter2gb = {'Month': 'M', 'Week': 'W-MON', 'Day': 'D'}[filter_period]

placeholder = st.empty()

while True:
    df = get_data()

    real_types = df['Type'].dropna().unique().tolist()
    cur_colors = choices(hex_colors, k=len(real_types))
    type2color = {rt: col for rt, col in zip(real_types, cur_colors)}
    date = pd.Timestamp.now()

    with placeholder.container():
        kpi_list = st.columns(len(real_types) * 2)

        for i, kpi in enumerate(kpi_list[:len(real_types)]):
            val = len(df[df['Type'] == real_types[i]])
            d = val - len(df[:-1][df['Type'] == real_types[i]])
            kpi.metric(label=f"{real_types[i]}s count", value=val, delta=d)

        for i, kpi in enumerate(kpi_list[len(real_types):]):
            prev_date = df[df['Type'] == real_types[i]]['Date'].values[-1]
            d = int(round((date - prev_date) / np.timedelta64(1, 'h'), 2) + 3)
            if d >= 24:
                r = requests.get(url=url_base + f"You didn't {real_types[i]} for {d} hours" + url_end)
            kpi.metric(
                label=f"Hours from last {real_types[i]}",
                value=d,
            )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<h4 style='text-align: center;'>{filter_type} distribution per Day</h4>", unsafe_allow_html=True)
            df_vis = df if filter_type == 'All' else df[df['Type'] == filter_type]
            df_vis['Time'] = df_vis['Date'].dt.time
            df_vis = df_vis.sort_values('Time')
            df_vis['Seconds'] = df_vis['Time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
            df_vis['Percent'] = (df_vis['Seconds'] / 86400 * 100).astype('int')
            # df_vis['Time'] = df_vis['Time'].apply(lambda x: x.strftime('%H:%M'))
            df_vis['Y'] = 0.5

            for x in df_vis['Percent'].unique():
                idx = df_vis[df_vis['Percent'] == x].index
                vals = get_d(len(idx))
                df_vis.loc[idx, 'Y'] = df_vis.loc[idx, 'Y'].values + vals

            fig1 = px.scatter(data_frame=df_vis, y='Y', x='Percent', color='Type', hover_data=['Time'], range_y=[0, 1])
            fig1.update_layout(legend=dict(yanchor="top", y=1.2, xanchor="left", x=0.01))
            fig1.update_layout(margin=dict(l=50, r=150))
            fig1.update_yaxes(nticks=5)

            for i in range(len(fig1.data)):
                name = fig1.data[i].name
                fig1.data[i].marker.color = type2color[name]

            st.write(fig1)

        with col2:
            st.markdown(f"<h4 style='text-align: center;'>Bar chart by {filter_period}</h1>", unsafe_allow_html=True)
            df_gb = df.groupby(pd.Grouper(key='Date', freq=filter2gb))['Type'].value_counts().reset_index()
            fig2 = px.bar(data_frame=df_gb, y='count', x='Date', color='Type')
            fig2.update_layout(legend=dict(yanchor="top", y=1.2, xanchor="left", x=0.01))
            fig2.update_layout(margin=dict(l=50, r=50))
            fig2.update_yaxes(nticks=5)

            for i in range(len(fig2.data)):
                name = fig2.data[i].name
                fig2.data[i].marker.color = type2color[name]

            st.write(fig2)

        st.markdown("### Full Table")
        st.dataframe(df)

    time.sleep(3600)
