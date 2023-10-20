import streamlit as st
import duckdb

## Load up database
con = duckdb.connect()
data_path = '../readings.parquet'
print("Loading data")
con.sql(f"CREATE TABLE readings as SELECT * FROM "{data_path};")
df = con.sql("SELECT * FROM readings LIMIT 10;").df()

## App
st.title('Test app')
st.dataframe(df)
