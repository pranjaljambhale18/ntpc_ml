import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("ntpc_model.pkl")


if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []

st.set_page_config(page_title="NTPC Predictor", layout="centered")
st.title("🔮 NTPC Power & CO₂ Predictor")
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

    st.success("✅ Prediction Complete")
    st.metric("🔋 Predicted Power", f"{predicted_power:.2f} BU")
    st.metric("🌍 Predicted CO₂ Emissions", f"{predicted_co2:,.2f} Tonnes")
    st.metric("💰 Revenue", f"₹{revenue:,.2f} Cr")
    st.metric("🔥 Fuel Cost", f"₹{cost:,.2f} Cr")
    st.metric("📈 Estimated Profit", f"₹{profit:,.2f} Cr")



# ➕ Suggestion block
st.markdown("### 💡 Suggestions Based on Your Inputs")

suggestions = []

# 1. Profit improvement
if profit < 1000:
    suggestions.append("🔼 Consider increasing the average tariff or optimizing operational efficiency to boost profit.")

# 2. Fuel cost too high
if fuel_cost > 3.5:
    suggestions.append("💸 Fuel cost per unit seems high. Explore cost-effective fuel procurement or optimize plant heat rate.")

# 3. Low PLF
if plf < 70:
    suggestions.append("⚙️ Low PLF. Improve plant utilization to enhance power output and reduce per-unit cost.")

# 4. Low renewable share
if re_share < 25:
    suggestions.append("🌿 Low RE share. Integrating more renewable energy can help reduce carbon emissions.")

# 5. CO2 emissions very high
if predicted_co2 > 1000000:
    suggestions.append("🌍 High CO₂ emissions. Consider increasing RE share or improving combustion efficiency.")

# 6. Power output below threshold
if predicted_power < 200:
    suggestions.append("🔋 Power generation is relatively low. Check fuel availability or PLF for optimization.")

# 7. Negative or low profit
if profit < 0:
    suggestions.append("🔴 Loss-making scenario. Review tariff rates, fuel mix, and operational strategies.")


if suggestions:
    for s in suggestions:
        st.info(s)
else:
    st.success("✅ All performance indicators look good! Keep it up.")



if st.session_state.all_predictions:
    st.markdown("### 🗃️ All Predictions This Session")
    all_df = pd.concat(st.session_state.all_predictions, ignore_index=True)
    st.dataframe(all_df)

    csv_all = all_df.to_csv(index=False)

    st.download_button(
        label="📥 Download All Predictions as CSV",
        data=csv_all,
        file_name="all_ntpc_predictions.csv",
        mime="text/csv"
    )
