import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Tarbimise analüüs",
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
        font-size: 3rem;
        font-weight: 800;
        color: #1D1458;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
        color: #5D688A;
        font-size: 1.05rem;
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
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }

    .metric-value {
        color: #1D1458;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-unit {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1D1458;
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
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .segment-desc {
        color: #4A5678;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .segment-range {
        color: #13214D;
        font-size: 1rem;
        font-weight: 700;
    }

    .section-wrapper {
        border: 1px solid #E6EAF2;
        border-radius: 14px;
        overflow: hidden;
        background: white;
        margin-top: 1.2rem;
    }

    .section-header-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        background: #FBFCFF;
        border-bottom: 1px solid #E6EAF2;
    }

    .section-header {
        padding: 1rem 1.25rem;
        font-weight: 700;
        color: #4D5878;
        font-size: 1.05rem;
        border-right: 1px solid #E6EAF2;
    }

    .section-header:last-child {
        border-right: none;
    }

    .section-header.active {
        color: #5A27F2;
        border-bottom: 3px solid #5A27F2;
        background: white;
    }

    .panel-box {
        padding: 0.6rem 0.3rem 0.4rem 0.3rem;
    }

    .mini-metric-card {
        border: 1px solid #E6EAF2;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        background: #FAFBFE;
        min-height: 92px;
    }

    .mini-metric-label {
        color: #4A5678;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .mini-metric-value {
        color: #1D1458;
        font-size: 1.7rem;
        font-weight: 800;
    }

    .mini-metric-danger {
        color: #E24B4B;
        font-size: 1.7rem;
        font-weight: 800;
    }

    .info-box {
        background: #F4F7FF;
        border: 1px solid #DCE5FF;
        border-radius: 12px;
        padding: 0.95rem 1rem;
        color: #33415F;
        font-size: 0.96rem;
        margin-top: 1rem;
    }

    .subsection-title {
        color: #1D1458;
        font-size: 1.05rem;
        font-weight: 700;
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
PRICE_PATH = DATA_DIR / "spot_pricing_combined_sorted.csv"


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

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

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


@st.cache_data
def load_price_data():
    if not PRICE_PATH.exists():
        return None

    price_df = pd.read_csv(PRICE_PATH, sep=";")

    price_df["timestamp"] = pd.to_datetime(
        price_df["timestamp"],
        format="%d.%m.%Y %H:%M"
    )

    price_df["spot_price_incl_vat"] = (
        price_df["spot_price_incl_vat"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    price_df["price"] = price_df["spot_price_incl_vat"]
    price_df["hour_timestamp"] = price_df["timestamp"].dt.floor("h")

    return price_df


df = load_data()
price_df = load_price_data()

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
total_consumption = df["consumption_kwh"].sum()

period_start = df["date"].min().strftime("%d.%m.%Y")
period_end = df["date"].max().strftime("%d.%m.%Y")
period_text = f"{period_start} – {period_end}"

total_consumption_text = f"{total_consumption:,.2f}".replace(",", " ")


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
# 2. PRICE CORRELATION
# =========================================================
if price_df is not None and "timestamp" in df.columns:
    df_price = df.copy()
    df_price["hour_timestamp"] = df_price["timestamp"].dt.floor("h")

    df_price = df_price.merge(
        price_df[["hour_timestamp", "price"]],
        on="hour_timestamp",
        how="left"
    )

    price_correlation = (
        df_price.groupby("segment", observed=True)
        .apply(lambda x: x["consumption_kwh"].corr(x["price"]))
        .reset_index(name="correlation")
    )

    price_correlation["segment"] = pd.Categorical(
        price_correlation["segment"],
        categories=segment_order_lower,
        ordered=True
    )

    price_correlation = price_correlation.sort_values("segment")
    price_correlation["segment"] = price_correlation["segment"].astype(str).str.upper()
    price_correlation["correlation"] = price_correlation["correlation"].round(2)

else:
    price_correlation = pd.DataFrame({
        "segment": ["S", "M", "L", "XL"],
        "correlation": [0.0, 0.0, 0.0, 0.0]
    })


# =========================================================
# 2. PRICE REGRESSION
# =========================================================
regression_table = pd.DataFrame(columns=[
    "Segment",
    "Regressioonikordaja",
    "R²",
    "Tõlgendus"
])

if price_df is not None and "timestamp" in df.columns:
    df_reg = df.copy()
    df_reg["hour_timestamp"] = df_reg["timestamp"].dt.floor("h")

    df_reg = df_reg.merge(
        price_df[["hour_timestamp", "price"]],
        on="hour_timestamp",
        how="left"
    )

    df_reg = df_reg.dropna(subset=["price", "consumption_kwh", "segment"])

    regression_results = []

    for seg in segment_order_lower:
        seg_df = df_reg[df_reg["segment"].astype(str) == seg].copy()

        if len(seg_df) >= 2:
            X = seg_df[["price"]]
            y = seg_df["consumption_kwh"]

            model = LinearRegression()
            model.fit(X, y)

            y_pred = model.predict(X)
            coefficient = model.coef_[0]
            r2 = r2_score(y, y_pred)

            if abs(coefficient) < 0.001 or r2 < 0.01:
                interpretation = "Olulist mõju ei paista"
            elif coefficient < 0:
                interpretation = "Tarbimine võib veidi väheneda hinna tõustes"
            else:
                interpretation = "Tarbimine võib veidi suureneda hinna tõustes"

            regression_results.append({
                "Segment": seg.upper(),
                "Regressioonikordaja": round(coefficient, 6),
                "R²": round(r2, 4),
                "Tõlgendus": interpretation
            })

    regression_table = pd.DataFrame(regression_results)


# =========================================================
# 3. SEGMENT REVIEW
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
    review_candidates["estimated_annual_kwh"] = review_candidates["estimated_annual_kwh"].round(0)

    review_table = review_candidates[
        [
            "household_id",
            "current_segment",
            "suggested_segment",
            "avg_daily_kwh",
            "estimated_annual_kwh"
        ]
    ].rename(columns={
        "household_id": "Majapidamine",
        "current_segment": "Praegune segment",
        "suggested_segment": "Soovituslik segment",
        "avg_daily_kwh": "Keskmine päevane tarbimine, kWh",
        "estimated_annual_kwh": "Hinnanguline aastatarbimine, kWh"
    }).sort_values("Hinnanguline aastatarbimine, kWh", ascending=False)

    review_table["Vajab suuremat segmenti"] = (
        review_table["Soovituslik segment"].map(segment_rank) >
        review_table["Praegune segment"].map(segment_rank)
    )

    review_table = review_table.head(8)

else:
    different_count = 0
    review_pct = 0.0

    review_table = pd.DataFrame(columns=[
        "Majapidamine",
        "Praegune segment",
        "Soovituslik segment",
        "Keskmine päevane tarbimine, kWh",
        "Hinnanguline aastatarbimine, kWh",
        "Vajab suuremat segmenti"
    ])


# =========================================================
# CHARTS
# =========================================================
fig_variability = px.bar(
    segment_variability,
    x="avg_cv",
    y="segment",
    orientation="h",
    text="avg_cv",
    labels={
        "avg_cv": "Variatsioonikordaja",
        "segment": "Segment"
    }
)

fig_variability.update_traces(
    textposition="outside",
    marker_color="#5A27F2"
)

fig_variability.update_layout(
    height=380,
    margin=dict(l=10, r=30, t=10, b=10),
    xaxis_title="Variatsioonikordaja",
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


fig_corr = px.bar(
    price_correlation,
    x="correlation",
    y="segment",
    orientation="h",
    text="correlation",
    labels={
        "correlation": "Korrelatsioon",
        "segment": ""
    }
)

fig_corr.update_traces(
    textposition="outside",
    marker_color="#5A27F2"
)

fig_corr.update_layout(
    height=380,
    margin=dict(l=10, r=30, t=10, b=10),
    xaxis_title="Korrelatsioon",
    yaxis_title="",
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

fig_corr.update_xaxes(
    showgrid=True,
    gridcolor="#E9EDF5",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="#7A8093",
    range=[-0.10, 0.10]
)

fig_corr.update_yaxes(
    categoryorder="array",
    categoryarray=["XL", "L", "M", "S"]
)


# =========================================================
# PAGE HEADER
# =========================================================
st.markdown(
    '<div class="page-title">Tarbimise analüüs</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-subtitle">Ülevaade tarbimise varieeruvusest, börsihinna mõjust tarbimisele ja võimalikust segmendi ümberhindamisest.</div>',
    unsafe_allow_html=True
)


# =========================================================
# TOP KPI CARDS
# =========================================================
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Majapidamisi</div>
        <div class="metric-value">{household_count}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Periood</div>
        <div class="metric-value" style="font-size: 1.55rem;">{period_text}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Kogutarbimine</div>
        <div class="metric-value">{total_consumption_text} <span class="metric-unit">kWh</span></div>
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
        <div class="segment-desc">Korter</div>
        <div class="segment-range">&lt; 3 000 kWh aastas</div>
    </div>
    """, unsafe_allow_html=True)

with seg2:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">M</div>
        <div class="segment-desc">Suur korter / Väike maja</div>
        <div class="segment-range">3 000 – 6 000 kWh aastas</div>
    </div>
    """, unsafe_allow_html=True)

with seg3:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">L</div>
        <div class="segment-desc">Maja</div>
        <div class="segment-range">6 000 – 12 000 kWh aastas</div>
    </div>
    """, unsafe_allow_html=True)

with seg4:
    st.markdown("""
    <div class="segment-card">
        <div class="segment-name">XL</div>
        <div class="segment-desc">Suur maja</div>
        <div class="segment-range">&gt; 12 000 kWh aastas</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FAKE TAB HEADER
# =========================================================
st.markdown("""
<div class="section-wrapper">
    <div class="section-header-row">
        <div class="section-header active">1. Prognoositavus</div>
        <div class="section-header">2. Börsihinna mõju</div>
        <div class="section-header">3. Segmendi ülevaatus</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# THREE MAIN PANELS
# =========================================================
col1, col2, col3 = st.columns(3, gap="large")


# -------------------------
# PANEL 1
# -------------------------
with col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)

    st.markdown("### Kui stabiilne on eri segmentide tarbimine?")

    st.markdown("""
Tarbimise stabiilsust hinnatakse siin **variatsioonikordaja** abil. 
See näitab, kui palju majapidamise päevane elektritarbimine kõigub võrreldes tema enda keskmise päevase tarbimisega.

**Valem:**  
variatsioonikordaja = päevase tarbimise standardhälve / keskmine päevane tarbimine

Näiteks kui majapidamise keskmine päevane tarbimine on **10 kWh** ja päevase tarbimise standardhälve on **2 kWh**, siis:

**2 / 10 = 0.20**

Tõlgendus:
- **madalam variatsioonikordaja** tähendab stabiilsemat ja paremini prognoositavat tarbimist;
- **kõrgem variatsioonikordaja** tähendab muutlikumat ja raskemini prognoositavat tarbimist.

Elektripakkuja jaoks on see oluline, sest suurema kõikumisega segmenti on keerulisem ette prognoosida.
""")

    st.markdown(
        '<div class="subsection-title">Keskmine variatsioonikordaja segmentide lõikes</div>',
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
        ℹ️ <b>Kõige muutlikum segment on {most_variable}</b>, mille keskmine variatsioonikordaja on <b>{most_variable_value}</b>. 
        See tähendab, et selle segmendi päevane tarbimine kõigub võrreldes keskmise tarbimisega kõige rohkem.
        <br><br>
        <b>Kõige stabiilsem segment on {most_stable}</b>, mille keskmine variatsioonikordaja on <b>{most_stable_value}</b>. 
        Selle segmendi tarbimismuster on ühtlasem ja elektripakkujal lihtsam prognoosida.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# PANEL 2
# -------------------------
with col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)

    st.markdown("### Kas börsihind mõjutab tarbimist?")

    st.markdown("""
Siin uuritakse, kas kliendid tarbivad elektrit vähem siis, kui börsihind on kõrgem.

Selleks kasutatakse korrelatsiooni. Korrelatsioon näitab, kas börsihind ja tarbimine liiguvad koos:
- kui väärtus on negatiivne, on kõrgema hinna ajal tarbimine pigem väiksem;
- kui väärtus on positiivne, on kõrgema hinna ajal tarbimine pigem suurem;
- kui väärtus on nulli lähedal, siis tugevat seost ei ole.
""")

    st.markdown(
        '<div class="subsection-title">Korrelatsioon börsihinna ja tarbimise vahel</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    strongest_row = price_correlation.copy()
    strongest_row["abs_corr"] = strongest_row["correlation"].abs()
    strongest_row = strongest_row.sort_values("abs_corr", ascending=False).iloc[0]

    strongest_segment = strongest_row["segment"]
    strongest_corr = strongest_row["correlation"]

    st.markdown(f"""
<div class="info-box">
    ℹ️ Kõige tugevam korrelatsioon on segmendis <b>{strongest_segment}</b>, kuid ka see väärtus on ainult <b>{strongest_corr}</b>.
    <br><br>
    <b>Järeldus:</b> börsihinna ja tarbimise vahel ei paista olevat tugevat praktilist seost. 
    Sama tulemust kinnitas ka regressioonanalüüs. See tähendab, et tarbimismustrid ei tundu oluliselt mõjutatavad börsihinna kõikumisest, vähemalt mitte sellisel tasemel, mis oleks statistiliselt märkimisväärne.
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# PANEL 3
# -------------------------
with col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)

    st.markdown("### Mitu majapidamist võiks kuuluda teise segmenti?")

    st.markdown("""
Majapidamise keskmine päevane tarbimine teisendatakse hinnanguliseks aastatarbimiseks  
ja võrreldakse tüüpiliste segmentide tarbimisvahemikega.
""")

    m1, m2 = st.columns(2)

    with m1:
        st.markdown(f"""
        <div class="mini-metric-card">
            <div class="mini-metric-label">Ülevaatamist vajaks</div>
            <div class="mini-metric-value">{different_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="mini-metric-card">
            <div class="mini-metric-label">Osakaal</div>
            <div class="mini-metric-danger">{review_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="subsection-title">Ülevaatamist vajavad majapidamised</div>',
        unsafe_allow_html=True
    )

    if not review_table.empty:
        review_table_display = review_table.drop(columns=["Vajab suuremat segmenti"])

        def highlight_upgrade_rows(row):
            if review_table.loc[row.name, "Vajab suuremat segmenti"]:
                return ["background-color: #E8F7EE; color: #14532D;"] * len(row)
            return [""] * len(row)

        styled_review_table = review_table_display.style.apply(
            highlight_upgrade_rows,
            axis=1
        )

        st.dataframe(
            styled_review_table,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Ülevaatamist vajavaid majapidamisi ei leitud.")

    st.markdown("""
    <div class="info-box">
        ℹ️ Rohelisega on märgitud majapidamised, mille soovituslik segment on praegusest suurem. 
        See ei tähenda automaatselt segmendi muutmist, vaid annab nimekirja majapidamistest, mille tegelik tarbimine võiks vajada ülevaatamist.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)