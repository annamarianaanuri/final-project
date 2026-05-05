import streamlit as st
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from pathlib import Path

# sets the page title
st.set_page_config(page_title="Energy consumption", layout="wide")
st.title("Household energy consumption")

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "DataSources" / "real_electricity_consumption_sorted.csv"

# clears cache in every load and reads df in
@st.cache_data
def load_data():
    household_consumption = pd.read_csv(DATA_PATH)
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

