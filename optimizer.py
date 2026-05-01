import numpy as np
import pandas as pd
from scipy.optimize import minimize

PROVINCE_GRID_FACTORS = {
    "British Columbia": 0.015,
    "Alberta": 0.590,
    "Ontario": 0.030,
    "Quebec": 0.002,
    "Saskatchewan": 0.660,
}

GAS_EMISSION_FACTOR = 53.06  # kg CO2 per MMBtu, common engineering estimate


def calculate_metrics(
    electricity_kwh,
    gas_mmbtu,
    electricity_price,
    gas_price,
    grid_ef,
    gas_ef,
    carbon_price,
):
    energy_cost = electricity_kwh * electricity_price + gas_mmbtu * gas_price
    emissions_kg = electricity_kwh * grid_ef + gas_mmbtu * gas_ef
    carbon_cost = emissions_kg / 1000 * carbon_price
    total_cost = energy_cost + carbon_cost

    return {
        "electricity_kwh": electricity_kwh,
        "gas_mmbtu": gas_mmbtu,
        "energy_cost_cad": energy_cost,
        "emissions_kg": emissions_kg,
        "carbon_cost_cad": carbon_cost,
        "total_cost_cad": total_cost,
    }


def optimize_energy_mix(
    total_energy_mmbtu,
    electricity_price,
    gas_price,
    grid_ef,
    gas_ef,
    carbon_price,
    objective="balanced",
):
    # 1 MMBtu = 293.071 kWh
    kwh_per_mmbtu = 293.071

    def objective_function(x):
        electric_share = x[0]
        electricity_mmbtu = electric_share * total_energy_mmbtu
        gas_mmbtu = (1 - electric_share) * total_energy_mmbtu

        electricity_kwh = electricity_mmbtu * kwh_per_mmbtu

        result = calculate_metrics(
            electricity_kwh,
            gas_mmbtu,
            electricity_price,
            gas_price,
            grid_ef,
            gas_ef,
            carbon_price,
        )

        if objective == "cost":
            return result["total_cost_cad"]
        elif objective == "emissions":
            return result["emissions_kg"]
        else:
            normalized_cost = result["total_cost_cad"] / 10000
            normalized_emissions = result["emissions_kg"] / 10000
            return 0.5 * normalized_cost + 0.5 * normalized_emissions

    result = minimize(
        objective_function,
        x0=[0.5],
        bounds=[(0, 1)],
        method="SLSQP",
    )

    electric_share = result.x[0]
    electricity_mmbtu = electric_share * total_energy_mmbtu
    gas_mmbtu = (1 - electric_share) * total_energy_mmbtu
    electricity_kwh = electricity_mmbtu * kwh_per_mmbtu

    metrics = calculate_metrics(
        electricity_kwh,
        gas_mmbtu,
        electricity_price,
        gas_price,
        grid_ef,
        gas_ef,
        carbon_price,
    )

    metrics["electric_share"] = electric_share
    metrics["gas_share"] = 1 - electric_share

    return metrics


def generate_tradeoff_curve(
    total_energy_mmbtu,
    electricity_price,
    gas_price,
    grid_ef,
    gas_ef,
    carbon_price,
):
    rows = []
    kwh_per_mmbtu = 293.071

    for electric_share in np.linspace(0, 1, 51):
        electricity_mmbtu = electric_share * total_energy_mmbtu
        gas_mmbtu = (1 - electric_share) * total_energy_mmbtu
        electricity_kwh = electricity_mmbtu * kwh_per_mmbtu

        metrics = calculate_metrics(
            electricity_kwh,
            gas_mmbtu,
            electricity_price,
            gas_price,
            grid_ef,
            gas_ef,
            carbon_price,
        )

        metrics["electric_share"] = electric_share
        metrics["gas_share"] = 1 - electric_share
        rows.append(metrics)

    return pd.DataFrame(rows)