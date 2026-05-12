import streamlit as st
from PIL import Image


# Browser tag title 
st.set_page_config(page_title="Electricity Plan Optimizer", layout="wide")

# Page title
st.header("Selecting the Optimal Electricity Plan Based on Real Consumption Data")

# Course info
st.write("""
**Project Team:** Anna Maria Naanuri, Jaana Tsurkan, Rainer Koorem 

**Course:** Vali-it Andmetarkus! 2026""")

# Problem
st.subheader("The Problem")
st.write("""
Our client is an energy provider.

**The client lacks a tool to provide data-backed recommendations on which electricity plan
would be most cost-effective for any given household.**

While the client has internal hypotheses about which package types suit which customers best, these are not
 evidence-based conclusions.""")

# Overview
st.subheader("Project Approach")
st.write("""
This project analyzes real consumption data of 40 households alongside historical market prices and 
available electricity packages on Estonian market, ultimately providing a factual foundation for 
personalized electricity package recommendations.""")

# Data description
st.subheader("Data Sources")

st.write("""
         **Master Table**
         - 4 source files joined into one dataframe using timestamp
         - transformed into a parquet file""")


img = Image.open("../Screenshot 2026-05-11 135520.png")
st.image(img, caption="Data lineage", width=600)

# Analysis Logic
st.subheader("Analysis Logic & Methodology")
st.write("""
**The result is an interactive dashboard to enable exploration across three key dimensions:**
         
**Consumption Pattern Visualization**
- Uncover pattern predictability for plan suitability  
         
**Customer Segment Analysis**
- Filter and compare household groups (S, M, L, XL) by consumption characteristics
- Identify which plan types suit which segments best
         

**Individual Household Cost Comparison**
- Calculates total estimated costs for any household under all available spot and fixed-price plans
- Identifies which plan type minimizes cost for each household profile
         

**Cost Savings Exploration**
- Quantify potential savings by switching between plan types
- Segment findings by household profile for targeted recommendations
""")

st.divider()
st.write("**Second page:** Consumption Analysis | **Third page:** Electricity Plan Comparison")