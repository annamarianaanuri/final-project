# libraries and add-ons needed
import streamlit as st
import pandas as pd
import duckdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# sets the page title
st.set_page_config(page_title="Energy consumption", layout="wide")
st.title("Household energy consumption")

# runs the df once / NEEDS TO BE THE FIRST COMMAND ON PAGE
@st.cache_data

# reads df in
def load_data():
    household_consumption = pd.read_csv("real_electricity_consumption_sorted.csv") 
    # converts timestamp from str to datetime format 
    household_consumption["timestamp"] = pd.to_datetime(household_consumption["timestamp"], format='%d.%m.%Y %H:%M:%S')
    # extracts year / month / day / hour from timestamp 
    household_consumption["year"] = household_consumption["timestamp"].dt.year
    household_consumption["month"] = household_consumption["timestamp"].dt.month
    household_consumption["day"] = household_consumption["timestamp"].dt.day
    household_consumption["hour"] = household_consumption["timestamp"].dt.hour
 
    return household_consumption

# uses given df 
household_consumption = load_data()

# finds unique values from columns
all_households = sorted(household_consumption["household_id"].unique())
all_years = sorted(household_consumption["year"].unique())
all_months = sorted(household_consumption["month"].unique())
all_days = sorted(household_consumption["day"].unique())
all_hours = sorted(household_consumption["hour"].unique())

# adds a subtitle for the filters
st.subheader("Filters")

# defines the amount of filters and their positioning
fc1, fc2, fc3, fc4, fc5 = st.columns(5)

# defines the functions of each filter - multiple select & by default all selected
sel_households = fc1.multiselect("Household", options=all_households, default=all_households)
sel_years = fc2.multiselect("Year", options=all_years, default=all_years)
sel_months = fc3.multiselect("Month", options=all_months, default=all_months,
    # defines the selection as text for months
    format_func=lambda m: [
        "January","February","March","April","May","June","July","August","September",
        "October","November","December"][m - 1],)
sel_days = fc4.multiselect("Day", options=all_days, default=all_days)
sel_hours = fc5.multiselect("Hour", options=all_hours, default=all_hours)

# defines a filters' function: keep only the row(s) matching the filter(s)
# one or many filters can be used
filtered = household_consumption.copy()
if sel_households: filtered = filtered[filtered["household_id"].isin(sel_households)]
if sel_years: filtered = filtered[filtered["year"].isin(sel_years)]
if sel_months: filtered = filtered[filtered["month"].isin(sel_months)]
if sel_days: filtered = filtered[filtered["day"].isin(sel_days)]
if sel_hours: filtered = filtered[filtered["hour"].isin(sel_hours)]

# if no rows match selected filter
if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# OPTIONAL - adds a filter for x axis
view = st.radio("View by", options=["Year", "Month", "Day", "Time"], horizontal=True,)

# if previous step is used, matches view option to df column
VIEW_COL = {
    "Year":"year",
    "Month":"month",
    "Day":"day",
    "Time":"hour",}

# groups the filtered data by the chosen time column, then gives average consumption
col = VIEW_COL[view]
values = filtered.groupby(col)["consumption_kwh"].mean().sort_index()

# A slot is "peak" if its consumption is above mean + 0.75 × std deviation.
# 0.75 is the sensitivity — higher = fewer peaks, lower = more peaks.
mean = values.mean()
std = values.std()
threshold = mean + 0.75 * std
peaks = values >= threshold   

# defines diplayed values as kpi-s
kpis = {
    "total_points": len(filtered),
    "peak_slot": values.idxmax(),
    "max_value": values.max(),
    "threshold": threshold,}

# adds a colour for below peak value and peak value
NORMAL_COLOR = "#2475B0"
PEAK_COLOR   = "#DC3C28"

# defines when each color is shown: 
seg_colors = []
for i in range(len(values) - 1):
    left_peak  = peaks.iloc[i]
    right_peak = peaks.iloc[i + 1]
    seg_colors.append(PEAK_COLOR if (left_peak or right_peak) else NORMAL_COLOR)

# defines months' names 
MONTH_NAMES = ["January","February","March","April","May","June", "July","August","September",
               "October","November","December"]

# converts months format from numbers to text
def slot_to_label(slot, view):
    if view == "Month":
        return MONTH_NAMES[int(slot) - 1]
# converts hour format from hours to hours & minutes (incl 15/30/45)
    if view == "Time":
        hour = int(slot) // 4
        minute = (int(slot) % 4) * 15
        return f"{hour:02d}:{minute:02d}"

    return str(int(slot))

# converts months format from number to text in x axis
x_labels = [slot_to_label(s, view) for s in values.index]
x_pos = list(range(len(values)))

# st.columns splits the page into equal-width columns side by side
# st.metric renders a labeled number card
peak_slot_label = slot_to_label(kpis["peak_slot"], view)
peak_slot_label = slot_to_label(values.idxmax(), view)
n_peaks = int(peaks.sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selections included", f"{kpis['total_points']:,}")
col2.metric("Most active period", peak_slot_label)
col3.metric("Highest usage level", f"{kpis['max_value']:.2f} kWh")
col4.metric("High usage threshold", f"{kpis['threshold']:.2f} kWh")

