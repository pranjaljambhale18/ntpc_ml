import streamlit as st
import joblib
import numpy as np

# Load the model
model = joblib.load('ntpc_model.pkl')

# Set page title
st.set_page_config(page_title="NTPC Forecasting App", layout="centered")

st.title("🔋 NTPC Energy, Revenue & CO₂ Forecasting")
st.write("Enter today's values to predict power generation, revenue, cost & emissions.")

# Input fields
coal = st.number_input("Coal Received (MT)", min_value=0.0, format="%.2f")
gas = st.number_input("Gas Received (MT)", min_value=0.0, format="%.2f")
plf = st.slider("Plant Load Factor (%)", 0, 100, 85)
re_share = st.slider("Renewable Share (%)", 0, 100, 15)
tariff = st.number_input("Tariff (₹/kWh)", min_value=0.0, format="%.2f")

# Prediction button
if st.button("Predict"):
    # Prepare input
    input_data = np.array([[coal, gas, plf, re_share, tariff]])
    
    # Get prediction
    prediction = model.predict(input_data)[0]

    # Display results
    st.success("📊 Forecast Results:")
    st.write(f"🔌 **Power Generated**: {prediction[0]:.2f} BU")
    st.write(f"💰 **Revenue**: ₹{prediction[1]:,.2f}")
    st.write(f"🛢️ **Fuel Cost**: ₹{prediction[2]:,.2f}")
    st.write(f"🌍 **CO₂ Emissions**: {prediction[3]:,.2f} tonnes")
