## Selecting the Optimal Electricity Plan Based on Real Consumption Data 
Vali-IT Andmetarkus!  

Link to Streamlit - https://consumption-and-electricity-plan.streamlit.app/


### Overview of the customer and the problem statement

Our client is an Estonian energy provider.

Despite having access to market data and customer consumption history, the client currently lacks the tools to give data-backed recommendations on which electricity plan type — exchange-based (spot) or fixed-price — would be the most cost-effective for any given household. While the client has internal hypotheses about which plan types suit which customers best, these remain unverified assumptions rather than evidence-based conclusions. 

This project aims to close that gap by analysing real household consumption patterns alongside historical market prices and available plans on the Estonian market, ultimately providing a factual foundation for personalised electricity plan recommendations. 

### Analysis approach 

The central question is simple: which electricity plan would have cost a given household the least over the given time window?

**To answer this, we:**
- Take the real household consumption profiles and calculate what each household would have paid under each available plan
- Use historical spot prices from Elering.ee and plan pricing from Elektrihind.ee
- Clean and align all datasets to a common format and time frame
- Produce a clear, visual comparison showing which plan suits which household profile best
- This gives our client a factual basis for customer recommendations rather than untested assumptions.

### Data Governance

**Data Protection Framework**
This project works with four datasets: the clients customer consumption data, historical electricity spot market prices, fixed plan pricing and spot plan pricing.

**Public datasets** (Elering spot prices, Elektrihind.ee plan pricing) contain no personal information and raise no data protection considerations.

**Customer consumption data is handled as follows:**
- The household consumption dataset has been encoded by the client prior to sharing, meaning our team cannot identify any individual customers
- The data is used exclusively for this analysis and will not be shared further or used for any other purpose

### Data Dictionary

**Business Glossary**
<img width="754" height="492" alt="image" src="https://github.com/user-attachments/assets/3cdf748e-f468-4448-9069-01f3faee94a7" />

### Data Glossary

**Core Tables:**
- consumption.csv
- spot_market_price.csv
- spot_plans.csv
- fixed_plans.csv
- master_table.parquet

**Consumption datatable: consumption.csv**
<img width="805" height="399" alt="image" src="https://github.com/user-attachments/assets/ff77053d-87da-42a0-9642-33d34ac4486e" />

**Spot market prices datatable: spot_market_price.csv**
<img width="904" height="444" alt="image" src="https://github.com/user-attachments/assets/dc661c18-e996-43ff-af71-557984d923db" />

**Fixed plan prices datatable: fixed_plans.csv**
<img width="757" height="614" alt="image" src="https://github.com/user-attachments/assets/825a4d31-dfb3-4047-a00b-6b2499d9d1d2" />

**Spot plan prices datatable: spot_plans.csv**
<img width="815" height="531" alt="image" src="https://github.com/user-attachments/assets/ce90a917-71a8-4f4a-aa86-97dab121eaf1" />

**Master table to calculate the optimal plans: master_table.parquet**
<img width="749" height="680" alt="image" src="https://github.com/user-attachments/assets/2e7bfe21-d6a2-433d-b48d-72bdc0858d8b" />

### Data lineage
<img width="922" height="558" alt="image" src="https://github.com/user-attachments/assets/fa62a653-fa4d-4955-8080-bce615b9813b" />

### Data Processing

**Data Quality & Transformations**
Several transformations were applied to align datasets across the consumption data time period:
- Time zone handling: Elering market price data is in Estonian time zone (EET/EEST). Daylight saving time transitions (clock shifts) created duplicate and missing hourly records, which were handled appropriately.
- Currency standardization: Spot price values were converted from cents/kWh to EUR/kWh for consistency across datasets.
- Column additions: Timestamps were split into separate date and time columns for easier analysis and aggregation.
- Language translations: All column names originally in Estonian were translated into English.

### Descriptive Report & Analysis
**Interactive Analysis Tool (Streamlit Dashboard)**
To make these findings actionable for the client’s team, an interactive Streamlit dashboard was built to enable exploration of the analysis across multiple dimensions.

**Core Functionality:**
- Individual household cost comparison — view total estimated costs for any household under spot and fixed-price plan options
- Consumption pattern visualization — explore seasonal trends, daily/hourly consumption profiles, and consumption variability across the customer base
- Customer segment analysis — filter and compare household groups by consumption characteristics to identify which plan types suit which segments best
- Cost savings exploration — see potential savings by switching between plan types, segmented by household profile

### Analysis Results

**The result is an interactive streamlit dashboard, enabling exploration across three key dimensions:**

**Consumption Pattern Visualization**
- Uncover pattern predictability for plan suitability

**Customer Segment Analysis**
- Filter and compare household groups (S, M, L, XL) by consumption characteristics
- Identify which plan types suit which segments best

**Individual Household Cost Comparison**
- Calculates total estimated costs for any household under all available spot and fixed-price plans
- Identifies which plan type minimizes cost for each household profile
