import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Consumption Analysis",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    h1, h2, h3, h4 {
        color: #13214D;
    }

    .page-title {
        font-size: 3.3rem;
        font-weight: 800;
        color: #1D1458;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
        color: #5D688A;
        font-size: 1.15rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        border: 1px solid #E6EAF2;
        border-radius: 14px;
        padding: 1.2rem 1.3rem;
        background: white;
        min-height: 120px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    .metric-label {
        color: #4A5678;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }

    .metric-value {
        color: #1D1458;
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .segment-card {
        border: 1px solid #E6EAF2;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: #FAFBFE;
        min-height: 105px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    .segment-name {
        color: #5A27F2;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .segment-desc {
        color: #4A5678;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .segment-range {
        color: #13214D;
        font-size: 1.05rem;
        font-weight: 700;
    }

    .analysis-section {
        border: 1px solid #E6EAF2;
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        background: white;
        margin-top: 1.4rem;
    }

    .analysis-label {
        color: #5A27F2;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .analysis-title {
        color: #2F2F3D;
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.18;
        margin-top: 1.1rem;
        margin-bottom: 1rem;
    }

    .analysis-text {
        color: #3D4052;
        font-size: 1.15rem;
        line-height: 1.75;
    }

    .analysis-text li {
        margin-bottom: 0.35rem;
    }

    .mini-metric-card {
        border: 1px solid #E6EAF2;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        background: #FAFBFE;
        min-height: 96px;
    }

    .mini-metric-label {
        color: #4A5678;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .mini-metric-value {
        color: #1D1458;
        font-size: 1.9rem;
        font-weight: 800;
    }

    .mini-metric-danger {
        color: #E24B4B;
        font-size: 1.9rem;
        font-weight: 800;
    }

    .info-box {
        background: #F4F7FF;
        border: 1px solid #DCE5FF;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        color: #33415F;
        font-size: 1.05rem;
        line-height: 1.55;
        margin-top: 1rem;
    }

    .subsection-title {
        color: #1D1458;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }

    .stDataFrame, .stTable {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "DataSources"

CONSUMPTION_PATH = DATA_DIR / "consumption_df_enriched.parquet"


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    if not CONSUMPTION_PATH.exists():
        st.error(f"File not found: {CONSUMPTION_PATH}")
        st.stop()

    df = pd.read_parquet(CONSUMPTION_PATH)

    df["date"] = pd.to_datetime(df["date"])

    df["client_segment"] = pd.Categorical(
        df["client_segment"].astype(str).str.upper(),
        categories=["S", "M", "L", "XL"],
        ordered=True
    )

    df["segment"] = df["client_segment"].astype(str).str.lower()

    df["segment"] = pd.Categorical(
        df["segment"],
        categories=["s", "m", "l", "xl"],
        ordered=True
    )

    return df


df = load_data()

segment_order_lower = ["s", "m", "l", "xl"]

segment_rank = {
    "S": 1,
    "M": 2,
    "L": 3,
    "XL": 4
}


# =========================================================
# KPI VALUES
# =========================================================
household_count = df["household_id"].nunique()

period_start = df["date"].min().strftime("%d.%m.%Y")
period_end = df["date"].max().strftime("%d.%m.%Y")
period_text = f"{period_start} – {period_end}"


# =========================================================
# 1. SEGMENT VARIABILITY
# =========================================================
daily_client = (
    df.groupby(["segment", "household_id", "date"], observed=False)["consumption_kwh"]
    .sum()
    .reset_index(name="daily_kwh")
)

client_variability = (
    daily_client.groupby(["segment", "household_id"], observed=False)
    .agg(
        avg_daily_kwh=("daily_kwh", "mean"),
        std_daily_kwh=("daily_kwh", "std")
    )
    .reset_index()
)

client_variability["cv"] = (
    client_variability["std_daily_kwh"] /
    client_variability["avg_daily_kwh"]
)

segment_variability = (
    client_variability.groupby("segment", observed=False)
    .agg(avg_cv=("cv", "mean"))
    .reset_index()
)

segment_variability["segment"] = pd.Categorical(
    segment_variability["segment"],
    categories=segment_order_lower,
    ordered=True
)

segment_variability = segment_variability.sort_values("segment")
segment_variability["segment"] = segment_variability["segment"].astype(str).str.upper()
segment_variability["avg_cv"] = segment_variability["avg_cv"].round(2)


# =========================================================
# 2. SEGMENT REVIEW
# =========================================================
household_daily = (
    df.groupby(["segment", "household_id", "date"], observed=True)["consumption_kwh"]
    .sum()
    .reset_index(name="daily_kwh")
)

household_avg = (
    household_daily.groupby(["segment", "household_id"], observed=True)
    .agg(avg_daily_kwh=("daily_kwh", "mean"))
    .reset_index()
)

household_avg["current_segment"] = household_avg["segment"].astype(str)

segment_medians = (
    household_avg.groupby("current_segment")["avg_daily_kwh"]
    .median()
    .reindex(segment_order_lower)
)

can_calculate_review = not segment_medians.isna().any()

if can_calculate_review:
    threshold_s_m = (segment_medians["s"] + segment_medians["m"]) / 2
    threshold_m_l = (segment_medians["m"] + segment_medians["l"]) / 2
    threshold_l_xl = (segment_medians["l"] + segment_medians["xl"]) / 2

    def suggest_segment(avg_daily_kwh):
        if avg_daily_kwh <= threshold_s_m:
            return "s"
        elif avg_daily_kwh <= threshold_m_l:
            return "m"
        elif avg_daily_kwh <= threshold_l_xl:
            return "l"
        else:
            return "xl"

    household_avg["suggested_segment"] = household_avg["avg_daily_kwh"].apply(suggest_segment)

    household_avg["different_segment"] = (
        household_avg["current_segment"] != household_avg["suggested_segment"]
    )

    household_avg["estimated_annual_kwh"] = household_avg["avg_daily_kwh"] * 365

    review_candidates = household_avg[household_avg["different_segment"]].copy()

    different_count = int(review_candidates["household_id"].nunique())
    review_pct = round(different_count / household_count * 100, 1) if household_count > 0 else 0.0

    review_candidates["current_segment"] = review_candidates["current_segment"].str.upper()
    review_candidates["suggested_segment"] = review_candidates["suggested_segment"].str.upper()
    review_candidates["avg_daily_kwh"] = review_candidates["avg_daily_kwh"].round(2)
    review_candidates["estimated_annual_kwh"] = review_candidates["estimated_annual_kwh"].round(2)

    review_table = review_candidates[
        [
            "household_id",
            "current_segment",
            "suggested_segment",
            "avg_daily_kwh",
            "estimated_annual_kwh"
        ]
    ].rename(columns={
        "household_id": "Household",
        "current_segment": "Current segment",
        "suggested_segment": "Suggested segment",
        "avg_daily_kwh": "Average daily consumption, kWh",
        "estimated_annual_kwh": "Estimated annual consumption, kWh"
    }).sort_values("Estimated annual consumption, kWh", ascending=False)

    review_table["Needs larger segment"] = (
        review_table["Suggested segment"].map(segment_rank) >
        review_table["Current segment"].map(segment_rank)
    )

else:
    different_count = 0
    review_pct = 0.0

    review_table = pd.DataFrame(columns=[
        "Household",
        "Current segment",
        "Suggested segment",
        "Average daily consumption, kWh",
        "Estimated annual consumption, kWh",
        "Needs larger segment"
    ])


# =========================================================
# CHART
# =========================================================
fig_variability = px.bar(
    segment_variability,
    x="avg_cv",
    y="segment",
    orientation="h",
    text="avg_cv",
    labels={
        "avg_cv": "Coefficient of variation",
        "segment": "Segment"
    }
)

fig_variability.update_traces(
    textposition="outside",
    marker_color="#5A27F2"
)

fig_variability.update_layout(
    height=390,
    margin=dict(l=10, r=30, t=10, b=10),
    xaxis_title="Coefficient of variation",
    yaxis_title="Segment",
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

fig_variability.update_yaxes(
    categoryorder="array",
    categoryarray=["XL", "L", "M", "S"]
)

fig_variability.update_xaxes(
    showgrid=True,
    gridcolor="#E9EDF5",
    zeroline=False
)


# =========================================================
# PAGE HEADER
# =========================================================
st.markdown(
    '<div class="page-title">Consumption Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-subtitle">Overview of consumption predictability and potential segment reassessment.</div>',
    unsafe_allow_html=True
)


# =========================================================
# TOP KPI CARDS
# =========================================================
kpi1, kpi2 = st.columns(2)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Households</div>
        <div class="metric-value">{household_count}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Period</div>
        <div class="metric-value" style="font-size: 1.65rem;">{period_text}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SEGMENT RANGE CARDS
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

seg1, seg2, seg3, seg4 = st.columns(4)

with seg1:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">S</div>
        <div class="segment-desc">Apartment</div>
        <div class="segment-range">&lt; 3,000 kWh per year</div>
    </div>
    """, unsafe_allow_html=True)

with seg2:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">M</div>
        <div class="segment-desc">Large apartment / Small house</div>
        <div class="segment-range">3,000 – 6,000 kWh per year</div>
    </div>
    """, unsafe_allow_html=True)

with seg3:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">L</div>
        <div class="segment-desc">House</div>
        <div class="segment-range">6,000 – 12,000 kWh per year</div>
    </div>
    """, unsafe_allow_html=True)

with seg4:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">XL</div>
        <div class="segment-desc">Large house</div>
        <div class="segment-range">&gt; 12,000 kWh per year</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ANALYSIS 1: PREDICTABILITY
# =========================================================
st.markdown("""
<div class="analysis-section">
    <div class="analysis-label">1. Predictability</div>
</div>
""", unsafe_allow_html=True)

left1, right1 = st.columns([1, 1], gap="large")

with left1:
    st.markdown(
        '<div class="analysis-title">How stable is consumption across segments?</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="analysis-text">
    Consumption stability is assessed using the <b>coefficient of variation</b>. 
    It shows how much a household's daily electricity consumption fluctuates compared with its own average daily consumption.

    <br><br><b>Formula:</b><br>
    coefficient of variation = standard deviation of daily consumption / average daily consumption

    <ul>
        <li>a <b>lower coefficient of variation</b> means more stable and more predictable consumption;</li>
        <li>a <b>higher coefficient of variation</b> means more variable and harder-to-predict consumption.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with right1:
    st.markdown(
        '<div class="subsection-title">Average coefficient of variation by segment</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(fig_variability, use_container_width=True)

most_variable_row = segment_variability.sort_values("avg_cv", ascending=False).iloc[0]
most_stable_row = segment_variability.sort_values("avg_cv", ascending=True).iloc[0]

most_variable = most_variable_row["segment"]
most_stable = most_stable_row["segment"]

most_variable_value = most_variable_row["avg_cv"]
most_stable_value = most_stable_row["avg_cv"]

st.markdown(f"""
<div class="info-box">
    ℹ️ <b>The most variable segment is {most_variable}</b>, with an average coefficient of variation of <b>{most_variable_value}</b>. 
    This means that daily consumption in this segment fluctuates the most relative to its average consumption.
    <br><br>
    <b>The most stable segment is {most_stable}</b>, with an average coefficient of variation of <b>{most_stable_value}</b>. 
    Its consumption pattern is more consistent and easier for the electricity provider to forecast.
</div>
""", unsafe_allow_html=True)


# =========================================================
# ANALYSIS 2: SEGMENT REVIEW
# =========================================================
st.markdown("""
<div class="analysis-section">
    <div class="analysis-label">2. Segment Review</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="analysis-title">How many households could belong to a different segment?</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="analysis-text">
A household's average daily consumption is converted into estimated annual consumption 
and compared with the typical consumption ranges of the segments.
</div>
""", unsafe_allow_html=True)

m1, m2 = st.columns(2)

with m1:
    st.markdown(f"""
    <div class="mini-metric-card">
        <div class="mini-metric-label">Need review</div>
        <div class="mini-metric-value">{different_count}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="mini-metric-card">
        <div class="mini-metric-label">Share</div>
        <div class="mini-metric-danger">{review_pct:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="subsection-title">Households needing review</div>',
    unsafe_allow_html=True
)

if not review_table.empty:
    review_table_display = review_table.drop(columns=["Needs larger segment"])

    def highlight_upgrade_rows(row):
        if review_table.loc[row.name, "Needs larger segment"]:
            return ["background-color: #E8F7EE; color: #14532D;"] * len(row)
        return [""] * len(row)

    styled_review_table = (
        review_table_display.style
        .format({
            "Average daily consumption, kWh": "{:.2f}",
            "Estimated annual consumption, kWh": "{:.2f}"
        })
        .apply(highlight_upgrade_rows, axis=1)
    )

    st.dataframe(
        styled_review_table,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No households needing review were found.")

st.markdown("""
<div class="info-box">
    ℹ️ Rows highlighted in green represent households whose suggested segment is larger than their current segment.
</div>
""", unsafe_allow_html=True)