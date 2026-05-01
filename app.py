import streamlit as st
import plotly.express as px
from optimizer import (
    PROVINCE_GRID_FACTORS,
    GAS_EMISSION_FACTOR,
    optimize_energy_mix,
    generate_tradeoff_curve,
)

st.set_page_config(
    page_title="Canada Energy & Carbon Optimizer",
    layout="wide"
)

st.title("Canada Energy Cost & Carbon Optimization Tool")
st.write(
    "A decision tool for comparing industrial energy cost, CO₂ emissions, "
    "and carbon pricing impacts across Canadian provinces."
)

st.sidebar.header("Input Parameters")

province = st.sidebar.selectbox(
    "Select Province",
    list(PROVINCE_GRID_FACTORS.keys())
)

grid_ef = PROVINCE_GRID_FACTORS[province]

total_energy_mmbtu = st.sidebar.number_input(
    "Daily Energy Demand (MMBtu/day)",
    min_value=10.0,
    value=500.0,
    step=10.0
)

electricity_price = st.sidebar.number_input(
    "Electricity Price (CAD/kWh)",
    min_value=0.01,
    value=0.12,
    step=0.01
)

gas_price = st.sidebar.number_input(
    "Natural Gas Price (CAD/MMBtu)",
    min_value=1.0,
    value=4.0,
    step=0.5
)

carbon_price = st.sidebar.slider(
    "Carbon Price (CAD/tonne CO₂)",
    min_value=0,
    max_value=200,
    value=95,
    step=5
)

objective = st.sidebar.selectbox(
    "Optimization Objective",
    ["balanced", "cost", "emissions"]
)

st.sidebar.write(f"Grid emission factor: **{grid_ef} kg CO₂/kWh**")
st.sidebar.write(f"Gas emission factor: **{GAS_EMISSION_FACTOR} kg CO₂/MMBtu**")

result = optimize_energy_mix(
    total_energy_mmbtu=total_energy_mmbtu,
    electricity_price=electricity_price,
    gas_price=gas_price,
    grid_ef=grid_ef,
    gas_ef=GAS_EMISSION_FACTOR,
    carbon_price=carbon_price,
    objective=objective,
)

tradeoff_df = generate_tradeoff_curve(
    total_energy_mmbtu=total_energy_mmbtu,
    electricity_price=electricity_price,
    gas_price=gas_price,
    grid_ef=grid_ef,
    gas_ef=GAS_EMISSION_FACTOR,
    carbon_price=carbon_price,
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Cost", f"${result['total_cost_cad']:,.0f}/day")
col2.metric("Energy Cost", f"${result['energy_cost_cad']:,.0f}/day")
col3.metric("Carbon Cost", f"${result['carbon_cost_cad']:,.0f}/day")
col4.metric("Emissions", f"{result['emissions_kg']/1000:,.2f} t CO₂/day")

st.subheader("Optimal Energy Mix")

mix_col1, mix_col2 = st.columns(2)
mix_col1.metric("Electricity Share", f"{result['electric_share']*100:.1f}%")
mix_col2.metric("Natural Gas Share", f"{result['gas_share']*100:.1f}%")

st.subheader("Cost vs Emissions Trade-off")

fig = px.scatter(
    tradeoff_df,
    x="emissions_kg",
    y="total_cost_cad",
    color="electric_share",
    labels={
        "emissions_kg": "CO₂ Emissions (kg/day)",
        "total_cost_cad": "Total Cost (CAD/day)",
        "electric_share": "Electricity Share"
    },
    title=f"Trade-off Curve for {province}"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("AI Decision Summary")

if objective == "cost":
    focus = "minimizing total operating cost"
elif objective == "emissions":
    focus = "minimizing CO₂ emissions"
else:
    focus = "balancing cost and emissions"

summary = f"""
For a facility in {province}, the optimized strategy focuses on {focus}.
At a carbon price of ${carbon_price}/tonne CO₂, the model recommends using
{result['electric_share']*100:.1f}% electricity and {result['gas_share']*100:.1f}% natural gas.

This results in an estimated daily cost of ${result['total_cost_cad']:,.0f}
and emissions of {result['emissions_kg']/1000:,.2f} tonnes CO₂ per day.

The trade-off curve shows how regional electricity emissions and carbon pricing
can shift the preferred energy mix.
"""

st.write(summary)

csv = tradeoff_df.to_csv(index=False)
st.download_button(
    "Download Trade-off Results as CSV",
    csv,
    "tradeoff_results.csv",
    "text/csv"
)