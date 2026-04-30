import streamlit as st
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from pathlib import Path


st.set_page_config(
    page_title="Electricity Package Analysis",
    layout="wide"
)

st.title("Electricity Package Cost Comparison")
st.write(
    "This dashboard compares household electricity costs under spot-based "
    "and fixed-price electricity packages."
)


@st.cache_data
def load_data():
    folder = Path(r"https://raw.githubusercontent.com/annamarianaanuri/final-project/refs/heads/main/DataSources/price_calculated_draft.csv")
    data = pd.read_csv(folder)

    if "Unnamed: 0" in data.columns:
        data = data.drop(columns=["Unnamed: 0"])

    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        format="%d.%m.%Y %H:%M:%S"
    )

    data["date"] = pd.to_datetime(
        data["date"],
        format="%d.%m.%Y"
    )

    data["spot_price_calculated"] = data["spot_price_calculated"].clip(lower=0)

    data = data.rename(columns={
        "spot_price_calculated": "cost_spot",
        "fixed_price_calculated_vendor_1": "cost_fixed_vendor_1",
        "fixed_price_calculated_vendor_2": "cost_fixed_vendor_2"
    })

    return data

consumption = load_data()

st.subheader("Data preview")

st.write("Shape of the dataset:")
st.write(consumption.shape)

st.write("First rows:")
st.dataframe(consumption.head(), use_container_width=True)


st.header("Dataset overview")

number_of_households = consumption["household_id"].nunique()
number_of_observations = len(consumption)
total_consumption_kwh = consumption["consumption_kwh"].sum()
start_date = consumption["timestamp"].min()
end_date = consumption["timestamp"].max()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Households", number_of_households)
col2.metric("Observations", f"{number_of_observations:,}")
col3.metric("Total consumption, kWh", f"{total_consumption_kwh:,.0f}")
col4.metric("Period", f"{start_date.date()} to {end_date.date()}")

st.header("Household-level cost comparison")

household_costs = consumption.groupby("household_id").agg(
    total_consumption_kwh=("consumption_kwh", "sum"),
    total_cost_spot=("cost_spot", "sum"),
    total_cost_fixed_vendor_1=("cost_fixed_vendor_1", "sum"),
    total_cost_fixed_vendor_2=("cost_fixed_vendor_2", "sum"),
    observations=("timestamp", "count"),
    start_date=("timestamp", "min"),
    end_date=("timestamp", "max")
).reset_index()

cost_columns = [
    "total_cost_spot",
    "total_cost_fixed_vendor_1",
    "total_cost_fixed_vendor_2"
]

household_costs["cheapest_package"] = (
    household_costs[cost_columns]
    .idxmin(axis=1)
    .replace({
        "total_cost_spot": "spot",
        "total_cost_fixed_vendor_1": "fixed_vendor_1",
        "total_cost_fixed_vendor_2": "fixed_vendor_2"
    })
)

household_costs["spot_minus_fixed_vendor_2"] = (
    household_costs["total_cost_spot"]
    - household_costs["total_cost_fixed_vendor_2"]
)

st.dataframe(
    household_costs,
    use_container_width=True,
    hide_index=True
)

st.header("Cheapest package distribution")

cheapest_package_counts = household_costs["cheapest_package"].value_counts()

fig, ax = plt.subplots(figsize=(8, 5))

cheapest_package_counts.plot(kind="bar", ax=ax)

ax.set_title("Number of households by cheapest package")
ax.set_xlabel("Cheapest package")
ax.set_ylabel("Number of households")
ax.tick_params(axis="x", rotation=0)

st.pyplot(fig)


st.header("Total cost across all households")

total_costs = household_costs[
    [
        "total_cost_spot",
        "total_cost_fixed_vendor_1",
        "total_cost_fixed_vendor_2"
    ]
].sum()

fig, ax = plt.subplots(figsize=(8, 5))

total_costs.plot(kind="bar", ax=ax)

ax.set_title("Total cost across all households by package")
ax.set_xlabel("Package")
ax.set_ylabel("Total cost, EUR")
ax.tick_params(axis="x", rotation=0)

st.pyplot(fig)



st.header("Cost difference: spot minus fixed vendor 2")

plot_data = household_costs.sort_values("spot_minus_fixed_vendor_2")

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(
    plot_data["household_id"],
    plot_data["spot_minus_fixed_vendor_2"]
)

ax.axhline(0)

ax.set_title("Cost difference: spot minus fixed vendor 2")
ax.set_xlabel("Household ID")
ax.set_ylabel("Cost difference, EUR")
ax.tick_params(axis="x", rotation=90)

st.pyplot(fig)

st.write(
    "Values above zero mean that fixed vendor 2 was cheaper. "
    "Values below zero mean that spot was cheaper."
)
