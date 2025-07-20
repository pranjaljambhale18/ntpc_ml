# app.py

import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load trained model
model = joblib.load("ntpc_model.pkl")

st.title("🔮 NTPC Power Generation & CO₂ Emission Predictor")

st.markdown("Provide input values below to predict power generation, CO₂ emissions, revenue, and profit.")

# Input form
with st.form("prediction_form"):
    installed_capacity = st.number_input("Installed Capacity (MW)", value=60000)
    coal_received = st.number_input("Coal Received (MTPA)", value=18500000)
    gas_received = st.number_input("Gas Received (MMSCM)", value=3000)
    plf = st.slider("PLF (%)", min_value=0, max_value=100, value=72)
    fuel_cost = st.number_input("Fuel Cost per Unit (₹/kWh)", value=3.2)
    tariff = st.number_input("Average Tariff (₹/kWh)", value=4.0)
    re_share = st.slider("RE Share (%)", min_value=0, max_value=100, value=28)

    submitted = st.form_submit_button("Predict")

# Perform prediction
if submitted:
    input_data = pd.DataFrame([[
        installed_capacity, coal_received, gas_received, plf, fuel_cost, tariff, re_share
    ]], columns=[
        'Installed_Capacity_MW',
        'Coal_Received_MTPA',
        'Gas_Received_MMSCM',
        'PLF_Percentage',
        'Fuel_Cost_per_Unit',
        'Avg_Tariff (ECR)',
        'RE_Share_Percentage'
    ])

    prediction = model.predict(input_data)
    power, co2 = prediction[0]

    revenue = power * tariff * 100  # ₹ Cr
    cost = power * fuel_cost * 100  # ₹ Cr
    profit = revenue - cost

    # Results
    st.success("✅ Prediction Successful!")
    st.metric("🔋 Power Generated", f"{power:.2f} BU")
    st.metric("🌍 CO₂ Emissions", f"{co2:,.2f} tonnes")
    st.metric("💰 Revenue", f"₹{revenue:,.2f} Cr")
    st.metric("🔥 Fuel Cost", f"₹{cost:,.2f} Cr")
    st.metric("📈 Profit", f"₹{profit:,.2f} Cr")
