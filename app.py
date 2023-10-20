import streamlit as st
import duckdb
import plotly.express as px

## Load up database
con = duckdb.connect()
data_path = 'sample.parquet'
print("Loading data")
con.sql(f"CREATE TABLE readings as SELECT * FROM '{data_path}';")

## App
st.title('London Smart Meter Profiler')
ids = con.sql("SELECT DISTINCT(LCLid) as ids FROM readings;").df()
selected_id = st.selectbox("select id", ids['ids'])


## Plot avg profile

df = con.sql(f"SELECT hour(DateTime) as hour, avg(reading_value) as reading FROM readings WHERE LCLid = '{selected_id}' GROUP BY hour(DateTime);").df()
st.plotly_chart(px.line(df, x='hour', y='reading'))
