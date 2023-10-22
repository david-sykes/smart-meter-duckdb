import streamlit as st
import duckdb
import plotly.express as px

## Load up database
@st.cache_resource
def load_database():
    con = duckdb.connect()
    data_path = '../readings'
    print("Loading data")
    con.sql(f"IMPORT DATABASE '{data_path}';")
    return con

con = load_database()

## App
st.title('London Smart Meter Profiler')
ids = con.sql("SELECT DISTINCT(LCLid) as ids FROM readings;").df()
selected_id = st.selectbox("select id", ids['ids'])

## Calculate key stats
stats_container_1 = st.container()
col1, col2 = stats_container_1.columns(2)
stats_container_2 = st.container()
col3, col4 = stats_container_1.columns(2)
peak = con.sql(f"SELECT SUM(reading_value) FILTER (hour(Datetime) IN (16,17,18,19)) /  sum(reading_value) FROM readings WHERE LCLid = '{selected_id}';").df()
night = con.sql(f"SELECT SUM(reading_value) FILTER (hour(Datetime) IN (22,23,24,0,1,2,3,4,5)) /  sum(reading_value) FROM readings WHERE LCLid = '{selected_id}';").df()
max = con.sql(f"SELECT MAX(reading_value) FROM readings WHERE LCLid = '{selected_id}';").df()
avg = con.sql(f"SELECT avg(reading_value) FROM readings WHERE LCLid = '{selected_id}';").df()

col1.metric("Peak consumption (4pm - 8pm):", f"{peak.iloc[0,0] * 100:.2f}%")
col2.metric("Night consumption (10pm - 6am):", f"{night.iloc[0,0] * 100:.2f}%")
col3.metric("Max half hourly consumption:", f"{max.iloc[0,0]:.2f} kWh")
col4.metric("Avg half hourly consumption:", f"{avg.iloc[0,0]:.2f} kWh")

## Plot avg profile

df = con.sql(f"SELECT hour(DateTime) as hour, avg(reading_value) as reading FROM readings WHERE LCLid = '{selected_id}' GROUP BY hour(DateTime);").df()
st.plotly_chart(px.line(df, x='hour', y='reading'))




