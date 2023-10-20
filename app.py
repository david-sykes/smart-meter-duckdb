import streamlit as st
import duckdb

## Load up database
con = duckdb.connect()

st.title('Test app')

