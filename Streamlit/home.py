import streamlit as st

# Browser tag title 
st.set_page_config(page_title="Electricity Package Optimizer", layout="wide")

# Page title
st.header("Selecting the Optimal Electricity Package Based on Real Consumption Data")

# Course info
st.write("""
**Project Team:** Anna Maria Naanuri, Jaana Tsurkan, Rainer Koorem 

**Course:** Vali-it Andmetarkus! 2026""")

# Problem
st.subheader("The Problem")
st.write("""
Our client is an Estonian renewable energy company dedicated to selling 100% renewable electricity to consumers in Estonia.

Despite having access to market data and customer consumption history, the client currently lacks the tools 
to provide data-backed recommendations on which package type — **exchange-based (spot)** or **fixed-price** — 
would be most cost-effective for any given household.

While the client has internal hypotheses about which package types suit which customers best, these remain 
**unverified assumptions** rather than evidence-based conclusions.""")

# Overview
st.subheader("Project Objective")
st.write("""
This project analyzes real consumption data of 40 households alongside historical market prices and 
available electricity packages on Estonian market, ultimately providing a factual foundation for 
personalized electricity package recommendations.""")

# Data description
st.subheader("Data Sources")
col1, col2 = st.columns(2)
with col1:
     st.write("""
    **Household Consumption Data**
    - Real consumption records from Estonian households
    - 30-minute interval granularity
    """)

with col2:
    st.write("""
    **Market Price Data**
    - Historical electricity spot prices Elering.ee
    - Fixed-price package offerings from Elektrihind.ee""")

# Analysis Logic
st.subheader("Analysis Logic")
st.write("""
1. **Consumption Pattern Analysis** - Examine household consumption segments to identify consumption variability within segments, 
segment consumption correlation to spot market prices, and household reorganizing to a better suited segment.

3. **Comparative Analysis** - Compare total costs across package options to identify both ends: maximum gain for the client, and
maximum savings for each household""")

st.divider()
st.write("**Second page:** Explore Consumption Patterns | **Third page:** Get Optimal Package Recommendations")