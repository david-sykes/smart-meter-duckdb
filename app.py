import streamlit as st
import duckdb

## Load up database
con = duckdb.connect()
data_path = '../readings.parquet'
print("Loading data")
con.sql(f"CREATE TABLE readings as SELECT * FROM '{data_path}';")

## App
st.title('Test app')
ids = con.sql("SELECT DISTINCT(LCLid) as ids FROM readings;").df()
selected_id = st.multiselect("select id", ids['ids'])
df = con.sql(f"SELECT * FROM readings WHERE LCLid = {selected_id};").df()
st.dataframe(df)
