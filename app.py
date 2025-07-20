import streamlit as st
import pandas as pd
import joblib

# Load trained model
model = joblib.load("ntpc_model.pkl")

# Initialize session state for storing all predictions
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# Page configuration
st.set_page_config(page_title="NTPC Prediction Dashboard", layout="centered")

st.title("NTPC Power & Emission Predictor")
st.markdown("This tool predicts power generation, CO₂ emissions, revenue, fuel cost, and estimated profit based on key operational inputs. It also gives actionable suggestions.")
st.markdown("---")
st.subheader("Enter Plant Inputs")

with st.form("prediction_form"):
    st.markdown("### Capacity & Resource Inputs")
    col1, col2 = st.columns(2)

    with col1:
        installed_capacity = st.number_input("Installed Capacity (MW)", value=60000, step=1000)
        coal_received = st.number_input("Coal Received (MTPA)", value=18500000, step=100000)
        gas_received = st.number_input("Gas Received (MMSCM)", value=3000, step=100)

    with col2:
        plf = st.slider("Plant Load Factor (PLF %)", min_value=0, max_value=100, value=72)
        re_share = st.slider("Renewable Energy Share (%)", min_value=0, max_value=100, value=28)

    st.markdown("### Financial Inputs")
    col3, col4 = st.columns(2)

    with col3:
        fuel_cost = st.number_input("Fuel Cost per Unit (₹/kWh)", value=3.2, step=0.1, format="%.2f")
    with col4:
        avg_tariff = st.number_input("Average Tariff (₹/kWh)", value=4.0, step=0.1, format="%.2f")

    submit = st.form_submit_button("Predict")

# When form is submitted
if submit:
    input_df = pd.DataFrame([[installed_capacity, coal_received, gas_received, plf, fuel_cost, avg_tariff, re_share]],
        columns=['Installed_Capacity_MW', 'Coal_Received_MTPA', 'Gas_Received_MMSCM', 'PLF_Percentage',
                 'Fuel_Cost_per_Unit', 'Avg_Tariff (ECR)', 'RE_Share_Percentage']
    )

    prediction = model.predict(input_df)
    predicted_power, predicted_co2 = prediction[0]

    revenue = predicted_power * avg_tariff * 100  # ₹ Cr
    cost = predicted_power * fuel_cost * 100      # ₹ Cr
    profit = revenue - cost

    # Save result to session state
    record = input_df.copy()
    record["Predicted_Power_BU"] = predicted_power
    record["CO2_Emissions_Tonnes"] = predicted_co2
    record["Revenue_Cr"] = revenue
    record["Fuel_Cost_Cr"] = cost
    record["Profit_Cr"] = profit

    st.session_state.prediction_history.append(record)

    # Show results
    st.markdown("## Prediction Results")
    st.success("Prediction complete based on your inputs.")

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric("Predicted Power", f"{predicted_power:.2f} BU")
    result_col2.metric("CO₂ Emissions", f"{predicted_co2:,.0f} Tonnes")
    result_col3.metric("Estimated Profit", f"₹{profit:,.2f} Cr")

    result_col4, result_col5 = st.columns(2)
    result_col4.metric("Revenue", f"₹{revenue:,.2f} Cr")
    result_col5.metric("Fuel Cost", f"₹{cost:,.2f} Cr")

    # Suggestions
    suggestions = []

    if predicted_power < 50:
        if plf < 70:
            suggestions.append("Predicted power is quite low. Consider increasing PLF or improving fuel availability.")
        else:
            suggestions.append("Predicted power is low despite good PLF. Check fuel availability or consider equipment upgrades.")

    if plf < 50:
        suggestions.append("PLF is very low. Increase utilization to boost power output and reduce per-unit cost.")
    elif 50 <= plf < 70:
        suggestions.append("PLF is below optimal range. Aim for above 70% to increase efficiency and revenue.")
    elif plf > 90:
        suggestions.append("Excellent PLF. Maintain good operational practices to keep this performance.")
        if predicted_co2 > 1_000_000:
            suggestions.append("You are running efficiently, but CO₂ emissions are high. Consider cleaner fuel or increase renewable share.")

    if predicted_co2 > 2_000_000:
        suggestions.append("CO₂ emissions are extremely high. Focus on emission control and cleaner fuels.")
    elif predicted_co2 > 1_000_000:
        suggestions.append("CO₂ emissions are above acceptable levels. Increase renewable share or optimize combustion processes.")

    if fuel_cost > 4:
        suggestions.append("Fuel cost is high. Consider switching to more economical fuel sources or increasing efficiency.")
    elif fuel_cost < 2:
        suggestions.append("Fuel cost is low. Try locking long-term contracts to maintain this advantage.")

    if re_share < 20:
        suggestions.append("Renewable energy share is low. Increasing it can reduce carbon footprint and long-term fuel cost.")
    elif re_share > 60:
        suggestions.append("High renewable energy share. Ensure grid stability and storage planning is in place.")

    if profit < 500:
        if avg_tariff < 3.5:
            suggestions.append("Estimated profit is low. Consider revisiting tariffs or operational efficiency.")
        if fuel_cost > 3.5:
            suggestions.append("High fuel cost is affecting profit. Negotiate fuel rates or increase efficiency.")

    if suggestions:
        st.markdown("## Suggestions Based on Inputs")
        st.info("Here are some suggestions to improve your KPIs:")
        for s in suggestions:
            st.markdown(f"- {s}")
    else:
        st.success("All parameters look optimal. Great job!")

# --- Download All Records ---
if st.session_state.prediction_history:
    st.markdown("---")
    st.subheader("Download All Predicted Records")
    full_df = pd.concat(st.session_state.prediction_history, ignore_index=True)
    csv_data = full_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download All Predictions as CSV",
        data=csv_data,
        file_name="ntpc_predictions.csv",
        mime="text/csv"
    )
