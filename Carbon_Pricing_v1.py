# Carbon_Pricing_Streamlit.py

import streamlit as st
import matplotlib.pyplot as plt

# Title
st.title("Forestry Carbon Project Revenue & NPV Model Demo")

st.markdown("""
This demo models carbon revenue from a reforestation project:
- Annual carbon sequestration × price
- Discounted over project duration (NPV)
""")

# --- User Inputs ---
carbon_price = st.slider('Carbon Price per ton (USD)', min_value=0, max_value=200, value=50)
annual_sequestration = st.slider('Annual Carbon Sequestration (tons CO₂-e/year)', min_value=0, max_value=10000, value=500)
project_years = st.slider('Project Duration (Years)', min_value=1, max_value=50, value=30)
discount_rate = st.slider('Discount Rate (%)', min_value=0.0, max_value=20.0, value=5.0)

# --- Model Calculations ---
cash_flows = []
undiscounted_flows = []
years = list(range(1, project_years + 1))

for year in years:
    annual_revenue = carbon_price * annual_sequestration
    discounted_revenue = annual_revenue / ((1 + discount_rate / 100) ** year)
    cash_flows.append(discounted_revenue)
    undiscounted_flows.append(annual_revenue)

total_revenue = sum(undiscounted_flows)
npv = sum(cash_flows)

# --- Output Summary ---
st.subheader("Results")
st.write(f"**Total Gross Revenue (undiscounted):** ${total_revenue:,.2f}")
st.write(f"**Net Present Value (NPV):** ${npv:,.2f}")

# --- Cash Flow Chart ---
st.subheader("Annual Discounted Cash Flows")

fig, ax = plt.subplots()
ax.bar(years, cash_flows, label="Discounted Revenue", alpha=0.8)
ax.set_xlabel("Year")
ax.set_ylabel("USD")
ax.set_title("Discounted Annual Carbon Revenue")
ax.legend()
st.pyplot(fig)

# Optional detail
if st.checkbox("Show Table of Annual Cash Flows"):
    for year, cash in zip(years, cash_flows):
        st.write(f"Year {year}: ${cash:,.2f}")

st.markdown("---")
st.caption("Note: This is a simplified model. Real forestry projects include costs, buffer pools, variable growth curves, and certification risks.")
