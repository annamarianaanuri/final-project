import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Consumption Analysis",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("📊 Consumption Analysis")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent.parent / 'Data Sources' / 'consumption_df_enriched.csv'
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert to categorical with custom order
    df['client_segment'] = pd.Categorical(
        df['client_segment'].str.upper(),
        categories=['S', 'M', 'L', 'XL'],
        ordered=True
    )
    
    df['season'] = pd.Categorical(
        df['season'],
        categories=['Spring', 'Summer', 'Fall', 'Winter'],
        ordered=True
    )
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(
        df['day_of_week'],
        categories=day_order,
        ordered=True
    )
    
    return df

df = load_data()

# Filters at the top in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("📅 Date Range")
    date_range = st.date_input(
        "Select dates",
        value=(df['date'].min().date(), df['date'].max().date()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date(),
        label_visibility="collapsed"
    )

with col2:
    st.subheader("🌍 Season(s)")
    seasons = st.multiselect(
        "Select seasons",
        options=df['season'].unique(),
        default=['Spring'],
        label_visibility="collapsed"
    )

with col3:
    st.subheader("📆 Day Type")
    day_type = st.radio(
        "Choose day type",
        options=["All", "Weekdays", "Weekends"],
        label_visibility="collapsed",
        horizontal=True
    )

with col4:
    st.subheader("📦 Segment(s)")
    segment = st.multiselect(
        "Select segments",
        options=sorted(df['client_segment'].unique()),
        default=['S'],
        label_visibility="collapsed"
    )

st.markdown("---")

# Apply filters
filtered_df = df[
    (df['date'].dt.date >= date_range[0]) &
    (df['date'].dt.date <= date_range[1]) &
    (df['season'].isin(seasons) if seasons else True) &
    (df['client_segment'].isin(segment) if segment else True)
]

if day_type == "Weekdays":
    filtered_df = filtered_df[~filtered_df['is_weekend']]
elif day_type == "Weekends":
    filtered_df = filtered_df[filtered_df['is_weekend']]

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(filtered_df))
with col2:
    st.metric("Total Consumption (kWh)", f"{filtered_df['consumption_kwh'].sum():.2f}")
with col3:
    st.metric("Avg Consumption (kWh)", f"{filtered_df['consumption_kwh'].mean():.2f}")

st.markdown("---")

st.subheader("Consumption Trends")

# Display KPI metrics at top
col1, col2, col3, col4 = st.columns(4)

with col1:
    segment_avg = filtered_df.groupby('client_segment')['consumption_kwh'].mean()
    if len(segment_avg) > 0:
        st.metric("Avg by Selected Segment", f"{segment_avg.iloc[0]:.3f} kWh")

with col2:
    season_avg = filtered_df.groupby('season')['consumption_kwh'].mean()
    if len(season_avg) > 0:
        st.metric("Avg by Selected Season", f"{season_avg.iloc[0]:.3f} kWh")

with col3:
    day_avg = filtered_df.groupby('day_of_week')['consumption_kwh'].mean()
    st.metric("Avg Consumption (Day)", f"{day_avg.mean():.3f} kWh")

with col4:
    hour_avg = filtered_df.groupby('hour')['consumption_kwh'].mean()
    st.metric("Avg Consumption (Hour)", f"{hour_avg.mean():.3f} kWh")

st.markdown("---")

# Create graphs
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# ===== SEGMENT GRAPH =====
all_segment_agg = df.groupby('client_segment')['consumption_kwh'].mean()
colors_segment = ['#e74c3c' if seg in segment else '#d3d3d3' for seg in all_segment_agg.index]
axes[0, 0].bar(all_segment_agg.index, all_segment_agg.values, color=colors_segment)
axes[0, 0].set_title('Average by Segment')

# ===== SEASON GRAPH =====
all_season_agg = df.groupby('season')['consumption_kwh'].mean()
colors_season = ['#e74c3c' if s in seasons else '#d3d3d3' for s in all_season_agg.index]
axes[0, 1].bar(all_season_agg.index, all_season_agg.values, color=colors_season)
axes[0, 1].set_title('Average by Season')

# ===== DAY OF WEEK =====
day_agg = filtered_df.groupby('day_of_week')['consumption_kwh'].mean()
axes[1, 0].bar(day_agg.index, day_agg.values, color='#e74c3c')
axes[1, 0].set_title('Average by Day of Week')

# ===== HOUR =====
hour_agg = filtered_df.groupby('hour')['consumption_kwh'].mean()
axes[1, 1].bar(hour_agg.index, hour_agg.values, color='#e74c3c')
axes[1, 1].set_title('Average by Hour')

plt.tight_layout()
st.pyplot(fig)