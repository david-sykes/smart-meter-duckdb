import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")


## Load up database
@st.cache_resource
def load_database():
    con = duckdb.connect()
    data_path = "../readings"
    print("Loading data")
    con.sql(f"IMPORT DATABASE '{data_path}';")
    return con


con = load_database()

## App
st.title("London Smart Meter Profiler")
ids = con.sql("SELECT DISTINCT(LCLid) as ids FROM readings;").df()

selected_id = st.selectbox("select id", ids["ids"])
st.divider()


stats_container = st.container()


stats_container.markdown("### Key stats:")
peak_col, night_col, max_col, avg_col = stats_container.columns(
    [0.25, 0.25, 0.25, 0.25]
)


## Calculate key stats
peak = con.sql(
    f"SELECT SUM(reading_value) FILTER (hour(Datetime) IN (16,17,18,19)) /  sum(reading_value) FROM readings WHERE LCLid = '{selected_id}';"
).df()
night = con.sql(
    f"SELECT SUM(reading_value) FILTER (hour(Datetime) IN (22,23,24,0,1,2,3,4,5)) /  sum(reading_value) FROM readings WHERE LCLid = '{selected_id}';"
).df()
max = con.sql(
    f"SELECT MAX(reading_value) FROM readings WHERE LCLid = '{selected_id}';"
).df()
avg = con.sql(
    f"SELECT avg(reading_value) FROM readings WHERE LCLid = '{selected_id}';"
).df()

peak_col.metric("Peak consumption (4pm - 8pm):", f"{peak.iloc[0,0] * 100:.2f}%")
night_col.metric("Night consumption (10pm - 6am):", f"{night.iloc[0,0] * 100:.2f}%")
max_col.metric("Max half hourly consumption:", f"{max.iloc[0,0]:.2f} kWh")
avg_col.metric("Avg half hourly consumption:", f"{avg.iloc[0,0]:.2f} kWh")

## Plot avg profile
st.divider()

charts_container = st.container()
daily_col, monthly_col = charts_container.columns([0.5, 0.5])


daily_col.markdown("#### Average daily profile")

df = con.sql(
    f"SELECT hour(DateTime) as hour, avg(reading_value) as reading FROM readings WHERE LCLid = '{selected_id}' GROUP BY hour(DateTime);"
).df()

avg_df = con.sql(
    f"SELECT hour(DateTime) as hour, avg(reading_value) as reading FROM readings GROUP BY hour(DateTime);"
).df()


hourly_fig = go.Figure()

hourly_fig.add_trace(
    go.Scatter(
        x=df["hour"],
        y=df["reading"],
        mode="lines+markers",
        name="Selected Meter ID Profile",
        marker_color="#007b7b",
    )
)

hourly_fig.add_trace(
    go.Scatter(
        x=avg_df["hour"],
        y=avg_df["reading"],
        mode="lines+markers",
        name="Average of all meters",
        marker_color="#9c9c9c",
    )
)

hourly_fig.update_layout(
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Hour of day",
    yaxis_title="Average consumption (kWh)",
)

daily_col.plotly_chart(hourly_fig, use_container_width=True, theme="streamlit")


## Plot monthly profile
monthly_col.markdown("#### Average monthly profile")

month_df = con.sql(
    f"""SELECT monthname(DateTime) as month, 
                   month(DateTime) as month_num,
                   sum(reading_value) as kwh 
                   FROM readings WHERE LCLid = '{selected_id}' GROUP BY 1,2 
                   ORDER BY 2;"""
).df()

avg_month_df = con.sql(
    f"""SELECT monthname(DateTime) as month, 
                   month(DateTime) as month_num,
                   sum(reading_value) / count(distinct(LCLid)) as kwh 
                   FROM readings GROUP BY 1,2 
                   ORDER BY 2;"""
).df()

bar_fig = go.Figure()
bar_fig.add_trace(
    go.Bar(
        x=month_df["month"],
        y=month_df["kwh"],
        name="Selected Meter ID monthly consumption",
        marker_color="#007b7b",
    )
)

bar_fig.add_trace(
    go.Scatter(
        x=avg_month_df["month"],
        y=avg_month_df["kwh"],
        name="Average of all meters",
        marker_color="#9c9c9c",
    )
)

bar_fig.update_layout(
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Hour of day",
    yaxis_title="Average consumption (kWh)",
)

monthly_col.plotly_chart(bar_fig, use_container_width=True)
