# energy-carbon-optimizer
# Canada Energy Cost & Carbon Optimization Tool

## Overview

This project is an interactive Python dashboard that evaluates industrial energy strategies based on operating cost, CO₂ emissions, and Canadian carbon pricing.

It is designed for a chemical or process facility that must choose between electricity and natural gas while considering regional electricity emissions and carbon costs.

## Why This Project Matters

Industrial companies in Canada face both energy cost pressure and emissions reduction targets. The optimal decision depends on location, electricity grid intensity, fuel prices, and carbon pricing.

This tool helps compare:
- Energy cost
- Carbon emissions
- Carbon pricing impact
- Optimal electricity vs natural gas mix
- Cost-emissions trade-offs

## Features

- Province selection: British Columbia, Alberta, Ontario, Quebec, Saskatchewan
- Electricity and natural gas cost inputs
- Carbon price input
- CO₂ emissions calculation
- Carbon cost calculation
- Constrained optimization using SciPy
- Cost vs emissions trade-off visualization
- Streamlit dashboard
- CSV export
- Automated decision summary

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- SciPy
- Plotly

## Engineering Model

The tool calculates:

Energy Cost = electricity use × electricity price + gas use × gas price
CO₂ Emissions = electricity use × grid emission factor + gas use × gas emission factor
Carbon Cost = CO₂ emissions × carbon price
Total Cost = Energy Cost + Carbon Cost