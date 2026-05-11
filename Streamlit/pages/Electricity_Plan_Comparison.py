import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from huggingface_hub import hf_hub_download, list_repo_files
import os

st.set_page_config(page_title="Electricity Plan Comparison", layout="wide")
st.title("Electricity Plan Comparison")

# 1. households list
households = [f"{size}-{i}" for size in ['s', 'm', 'l', 'xl'] for i in range(1, 11)]

# 2. Original load_data function
#@st.cache_data
#def load_data(household, start, end):
 #   return pd.read_parquet(
  #      "optimal_plan_partitioned",
   #     filters=[
    #        ("household_id", "=", household),
     #       ("timestamp", ">=", pd.Timestamp(start)),
      #      ("timestamp", "<", pd.Timestamp(end))
       # ]
    #)

# 2. Loading the data from Hugging Face
@st.cache_data
def load_data(household, start, end):
    all_files = list_repo_files(
        repo_id="rainerkoorem/electricity-plans",
        repo_type="dataset"
    )

    household_files = [
        f for f in all_files
        if f.startswith(f"master_table_partitioned/household_id={household}/")
        and f.endswith(".parquet")
    ]

    dfs = []
    for filename in household_files:
        local_path = hf_hub_download(
            repo_id="rainerkoorem/electricity-plans",
            filename=filename,
            repo_type="dataset"
        )
        dfs.append(pd.read_parquet(local_path))

    df = pd.concat(dfs, ignore_index=True)

    return df[
        (df['timestamp'] >= pd.Timestamp(start)) &
        (df['timestamp'] < pd.Timestamp(end))
    ]

# 3. filters
col1, col2, col3 = st.columns(3)
with col1:
    selected_household = st.selectbox("Household", sorted(households))
with col2:
    start_date = st.date_input("Start date", value=pd.Timestamp("2025-04-01"), format="DD.MM.YYYY")
with col3:
    end_date = st.date_input("End date", value=pd.Timestamp("2026-02-28"), format="DD.MM.YYYY")

st.divider()

# 4. load data using the filter values
df_filtered = load_data(selected_household, start_date, end_date)

# derive is_night_rate from timestamp
import holidays
estonian_holidays = holidays.Estonia(years=[2025, 2026])

# get unique timestamps to avoid recalculating per plan
df_consumption = df_filtered[df_filtered['plan_id'] == df_filtered['plan_id'].iloc[0]][['timestamp', 'consumption_kwh']].copy()

df_consumption['hour'] = df_consumption['timestamp'].dt.hour
df_consumption['is_daytime'] = (df_consumption['hour'] >= 7) & (df_consumption['hour'] < 22)
df_consumption['is_weekend'] = df_consumption['timestamp'].dt.dayofweek >= 5
df_consumption['is_public_holiday'] = df_consumption['timestamp'].dt.date.isin(estonian_holidays)
df_consumption['is_night_rate'] = ~df_consumption['is_daytime'] | df_consumption['is_weekend'] | df_consumption['is_public_holiday']

# metrics
total_consumption = df_consumption['consumption_kwh'].sum()
days_in_period = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1
avg_daily_consumption = total_consumption / days_in_period

day_consumption = df_consumption[~df_consumption['is_night_rate']]['consumption_kwh'].sum()
night_consumption = df_consumption[df_consumption['is_night_rate']]['consumption_kwh'].sum()
day_pct = (day_consumption / total_consumption * 100)
night_pct = (night_consumption / total_consumption * 100)



st.subheader(f"The plan prices for the household {selected_household}")
st.markdown("""
    This table shows the estimated total electricity cost for each available plan 
    over the selected time period, ranked from cheapest to most expensive.
    
    **How the total price is being calculated:**
    
    For **fixed plans**, the energy cost per 15-minute interval is determined by 
    the time of consumption. Daytime rate (07:00–22:00) applies on regular weekdays, 
    while the night rate applies during nighttime hours (22:00–07:00), on weekends 
    (Saturday and Sunday), and on Estonian public holidays — regardless of the time of day.
    
    For **spot plans**, the energy cost per interval is based on the Nord Pool 
    electricity market price at that exact moment, with the plan's fixed margin 
    added on top.
    
    For **all plans**, the monthly standing fee is prorated evenly across every 
    15-minute interval in the period and added to the energy cost.
    
    The **total price** is the sum of all interval costs over the selected time window.
            
    The data about the electricity plans used to calculate the total price is from 'https://elektrihind.ee/paketid/'.
            
    The data about the plans used is from **29th of April, 2026**.
            
    By default, the plans are listed in ascending order starting from the cheapest.
""")

# display
st.subheader(f"Consumption summary for {selected_household}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total consumption", f"{total_consumption:.0f} kWh")
with col2:
    st.metric("Avg daily consumption", f"{avg_daily_consumption:.2f} kWh")
with col3:
    st.metric("Daytime consumption", f"{day_pct:.1f}%")
with col4:
    st.metric("Night / weekend / holiday consumption", f"{night_pct:.1f}%")

# 5. aggregate and display
df_summary = (
    df_filtered
    .groupby(['plan_id', 'plan_name', 'vendor', 'plan_type', 'production_type'], as_index=False)['total_cost']
    .sum()
    .sort_values('total_cost')
    .reset_index(drop=True)
)

df_summary['total_cost'] = df_summary['total_cost'].round(2)
df_summary.index += 1

st.caption(f"{start_date} → {end_date} · {len(df_summary)} plans compared")

plan_type_col, spacer, production_type_col = st.columns([2, 0.5, 3])

with plan_type_col:
    st.markdown("<p style='font-size:12px; color:grey; margin-bottom:0px;'>Plan type</p>", unsafe_allow_html=True)
    pt_col1, pt_col2 = st.columns(2)
    with pt_col1:
        show_fixed = st.checkbox("Fixed", value=True)
    with pt_col2:
        show_spot = st.checkbox("Spot", value=True)

with production_type_col:
    st.markdown("<p style='font-size:12px; color:grey; margin-bottom:0px;'>Production type</p>", unsafe_allow_html=True)
    prt_col1, prt_col2, prt_col3 = st.columns(3)
    with prt_col1:
        show_tavaline = st.checkbox("Tavaline", value=True)
    with prt_col2:
        show_roheline = st.checkbox("Roheline", value=True)
    with prt_col3:
        show_kombineeritud = st.checkbox("Kombineeritud", value=True)

selected_plan_types = []
if show_fixed: selected_plan_types.append('fixed')
if show_spot: selected_plan_types.append('spot')

selected_production_types = []
if show_tavaline: selected_production_types.append('tavaline')
if show_roheline: selected_production_types.append('roheline')
if show_kombineeritud: selected_production_types.append('kombineeritud')

df_summary = df_summary[
    (df_summary['plan_type'].isin(selected_plan_types)) &
    (df_summary['production_type'].isin(selected_production_types))
]


min_cost = df_summary['total_cost'].min()

df_summary['Difference'] = df_summary['total_cost'].apply(
    lambda x: "✅ cheapest" if x == min_cost else f"🔴 +€{(x - min_cost):.2f}"
)

df_summary['Total price'] = df_summary['total_cost'].apply(lambda x: f"€{x:.2f}")
df_summary = df_summary.drop(columns=['plan_id', 'total_cost'])

df_summary = df_summary.rename(columns={
    'plan_name': 'Plan',
    'vendor': 'Provider',
    'plan_type': 'Plan type',
    'production_type': 'Production type'
})

df_summary = df_summary[['Plan', 'Provider', 'Plan type', 'Production type', 'Total price', 'Difference']]

st.dataframe(df_summary, use_container_width=True)








# Secondary chart
st.divider()
st.subheader("Monthly cost breakdown")
st.markdown("""
    This chart compares the monthly prices of the selected plans and visualizes the household electricity consumption over given time window.
            
    By default, the cheapest fixed plan and the cheapest spot plan are being shown.
""")

# find cheapest fixed and spot plan by total cost
cheapest_fixed = (
    df_filtered[df_filtered['plan_type'] == 'fixed']
    .groupby('plan_name')['total_cost'].sum()
    .idxmin()
)

cheapest_spot = (
    df_filtered[df_filtered['plan_type'] == 'spot']
    .groupby('plan_name')['total_cost'].sum()
    .idxmin()
)

# 1. build plan_labels BEFORE the multiselect
plan_labels = (
    df_filtered.drop_duplicates('plan_name')
    .assign(label=lambda x: x['plan_name'] + ' · ' + x['vendor'] + ' · ' + x['plan_type'])
    .set_index('plan_name')['label']
)

# 2. multiselect using plan_labels
selected_plans = st.multiselect(
    "Select plans",
    options=sorted(plan_labels.values.tolist()),
    default=[plan_labels[cheapest_fixed], plan_labels[cheapest_spot]]
)

# 3. filter df using the selected labels
df_chart = df_filtered[df_filtered['plan_name'].isin(
    plan_labels[plan_labels.isin(selected_plans)].index
)]

# 4. aggregate to monthly totals — add consumption
df_monthly = (
    df_chart
    .assign(month=df_chart['timestamp'].dt.to_period('M').dt.to_timestamp())
    .groupby(['month', 'plan_name'], as_index=False)
    .agg(total_cost=('total_cost', 'sum'), consumption_kwh=('consumption_kwh', 'sum'))
    .sort_values('month')
)
df_monthly['total_cost'] = df_monthly['total_cost'].round(2)
df_monthly['consumption_kwh'] = df_monthly['consumption_kwh'].round(1)

# 5. add plan_label AFTER aggregation
df_monthly['plan_label'] = (
    df_monthly['plan_name'] + ' · ' +
    df_monthly['plan_name'].map(df_filtered.drop_duplicates('plan_name').set_index('plan_name')['vendor']) + ' · ' +
    df_monthly['plan_name'].map(df_filtered.drop_duplicates('plan_name').set_index('plan_name')['plan_type'])
)

# 6. chart

# get one consumption value per month (same across all plans)
df_consumption_monthly = df_monthly.drop_duplicates('month')[['month', 'consumption_kwh']]

fig = make_subplots(specs=[[{"secondary_y": True}]])

# add one bar trace per plan
for label in df_monthly['plan_label'].unique():
    df_plan = df_monthly[df_monthly['plan_label'] == label]
    fig.add_trace(
        go.Bar(
            x=df_plan['month'],
            y=df_plan['total_cost'],
            name=label,
            text=df_plan['total_cost'].apply(lambda x: f"€{x:.2f}"),
            textposition='outside'
        ),
        secondary_y=False
    )

# add consumption line on secondary axis — no text labels
fig.add_trace(
    go.Scatter(
        x=df_consumption_monthly['month'],
        y=df_consumption_monthly['consumption_kwh'],
        name='Consumption (kWh)',
        mode='lines+markers',
        line=dict(color='black', width=2),
        marker=dict(size=6)
    ),
    secondary_y=True
)

fig.update_layout(barmode='group')

# embed consumption figures into x-axis tick labels
fig.update_xaxes(
    ticktext=[
        f"{m.strftime('%b %Y')}<br>{c:.1f} kWh"
        for m, c in zip(df_consumption_monthly['month'], df_consumption_monthly['consumption_kwh'])
    ],
    tickvals=df_consumption_monthly['month'].tolist(),
    title=None
)

fig.update_yaxes(title_text="Total cost (€)", secondary_y=False)
fig.update_yaxes(title_text="Consumption (kWh)", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)



