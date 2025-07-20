import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("ntpc_model.pkl")

if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []

st.set_page_config(page_title="NTPC Predictor", layout="centered")
st.title("NTPC Power & CO₂ Predictor")
st.markdown("This app predicts power generation, CO₂ emissions, revenue, fuel cost, and profit based on your inputs.")

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        installed_capacity = st.number_input("Installed Capacity (MW)", value=60000)
        coal_received = st.number_input("Coal Received (MTPA)", value=18500000)
        gas_received = st.number_input("Gas Received (MMSCM)", value=3000)
        plf = st.slider("PLF (%)", 0, 100, 72)

    with col2:
        fuel_cost = st.number_input("Fuel Cost per Unit (₹/kWh)", value=3.2)
        avg_tariff = st.number_input("Average Tariff (₹/kWh)", value=4.0)
        re_share = st.slider("RE Share (%)", 0, 100, 28)

    submit = st.form_submit_button("Predict")

if submit:
    input_df = pd.DataFrame([[installed_capacity, coal_received, gas_received,
                               plf, fuel_cost, avg_tariff, re_share]],
                             columns=[
                                 'Installed_Capacity_MW',
                                 'Coal_Received_MTPA',
                                 'Gas_Received_MMSCM',
                                 'PLF_Percentage',
                                 'Fuel_Cost_per_Unit',
                                 'Avg_Tariff (ECR)',
                                 'RE_Share_Percentage'
                             ])

    prediction = model.predict(input_df)
    predicted_power, predicted_co2 = prediction[0]

    revenue = predicted_power * avg_tariff * 100
    cost = predicted_power * fuel_cost * 100
    profit = revenue - cost

    input_df["Predicted_Power_BU"] = predicted_power
    input_df["Predicted_CO2_Tonnes"] = predicted_co2
    input_df["Revenue_Cr"] = revenue
    input_df["Fuel_Cost_Cr"] = cost
    input_df["Profit_Cr"] = profit

    st.session_state.all_predictions.append(input_df)

    st.success("Prediction Complete")
    st.metric("Predicted Power", f"{predicted_power:.2f} BU")
    st.metric("Predicted CO₂ Emissions", f"{predicted_co2:,.2f} Tonnes")
    st.metric("Revenue", f"₹{revenue:,.2f} Cr")
    st.metric("Fuel Cost", f"₹{cost:,.2f} Cr")
    st.metric("Estimated Profit", f"₹{profit:,.2f} Cr")

    # Suggestions
    st.markdown("### Suggestions Based on Your Inputs")
    suggestions = []

    # Profit Related
    if profit < 0:
        suggestions.append("Your plant is operating at a loss. Consider increasing the average tariff or reducing fuel costs.")
    elif profit < 500:
        suggestions.append("Profit is low. Improving PLF or reducing operational wastage may help.")
    elif profit > 5000:
        suggestions.append("Excellent profit. Maintain current practices and explore further efficiency improvements.")

    # PLF Related
    if plf < 50:
        suggestions.append("PLF is very low. Increase utilization to boost power output and reduce per-unit cost.")
    elif 50 <= plf < 70:
        suggestions.append("PLF is below optimal range. Aim for above 70% to increase efficiency and revenue.")
    elif plf > 90:
        suggestions.append("Excellent PLF. Ensure maintenance practices continue supporting high utilization.")

    # Fuel Cost
    if fuel_cost > 4:
        suggestions.append("Fuel cost is high. Explore cheaper sources, optimize heat rate, or renegotiate fuel contracts.")
    elif fuel_cost < 2:
        suggestions.append("Fuel cost is very low. Maintain existing procurement efficiency.")

    # Avg Tariff
    if avg_tariff < 3.5:
        suggestions.append("Tariff is on the lower side. Consider tariff revision with regulators if justified.")
    elif avg_tariff > 5:
        suggestions.append("High tariff. This supports revenue but may need performance justification.")

    # RE Share
    if re_share < 20:
        suggestions.append("Renewable share is low. Increase renewable integration to lower carbon emissions.")
    elif re_share > 40:
        suggestions.append("Good renewable share. Continue focus on green energy initiatives.")

    # CO2 Emissions
    if predicted_co2 > 1_000_000:
        suggestions.append("CO₂ emissions are very high. Consider transitioning to cleaner fuel or increasing RE share.")
    elif predicted_co2 < 100000:
        suggestions.append("Excellent emission control. Sustain current fuel mix and efficiency levels.")

    # Coal & Gas Inputs
    if coal_received < 10000000:
        suggestions.append("Coal received is low. Ensure consistent fuel supply to maintain generation targets.")
    if gas_received < 1000:
        suggestions.append("Gas received is low. Check supply chain issues or consider fuel switching options.")

    # Power Output
    # Power-related suggestions
    if predicted_power < 50:
        if plf < 70:
            suggestions.append("Predicted power is quite low. Consider increasing PLF or improving fuel availability.")
        else:
            suggestions.append("Predicted power is low despite good PLF. Check fuel availability or consider equipment upgrades.")
)
    elif predicted_power > 500:
        suggestions.append("High power output. Continue optimizing performance.")

    # Installed Capacity
    if installed_capacity > 100000 and plf < 60:
        suggestions.append("High installed capacity with low PLF. Focus on better utilization of capacity.")

    if fuel_cost > 3 and profit < 500:
        suggestions.append("Fuel cost is high and profit is low. Optimize procurement and improve efficiency.")

    if avg_tariff < fuel_cost:
        suggestions.append("Average tariff is lower than fuel cost. This may lead to loss unless controlled.")

    if fuel_cost > 3.5 and plf < 60:
        suggestions.append("Both high fuel cost and low PLF are hurting profits. Address both urgently.")

    if re_share < 20 and predicted_co2 > 900000:
        suggestions.append("Increase RE share to control CO₂ emissions and improve sustainability rating.")

    if installed_capacity > 80000 and predicted_power < 200:
        suggestions.append("Installed capacity is underutilized. Investigate operational bottlenecks.")

    if plf > 90 and predicted_co2 > 1000000:
        suggestions.append("You are running at high efficiency (high PLF), but CO2 emissions are too high. Consider fuel with better emission quality or increase renewable share.")


    if suggestions:
        for s in suggestions:
            st.info(s)
    else:
        st.success("All performance indicators look within optimal range.")

# Past Predictions and Download
if st.session_state.all_predictions:
    st.markdown("### All Predictions This Session")
    all_df = pd.concat(st.session_state.all_predictions, ignore_index=True)
    st.dataframe(all_df)

    csv_all = all_df.to_csv(index=False)

    st.download_button(
        label="Download All Predictions as CSV",
        data=csv_all,
        file_name="all_ntpc_predictions.csv",
        mime="text/csv"
    )
