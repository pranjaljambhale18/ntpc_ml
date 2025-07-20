import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("ntpc_model.pkl")

# Maintain session history
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

# Profit-related
if profit < 1000:
    suggestions.append("📉 Profit is low. Try increasing average tariff or improving operational efficiency.")
if profit < 0:
    suggestions.append("🔴 Negative profit. Review your fuel cost and increase tariff if possible.")
if revenue < 1000:
    suggestions.append("💸 Low revenue. Consider boosting generation or negotiating higher tariffs.")
if revenue > 10000:
    suggestions.append("💰 Excellent revenue! Keep monitoring costs to maintain high profit.")
if cost > 9000:
    suggestions.append("💡 Fuel cost is very high. Try optimizing fuel mix or increasing efficiency.")

# PLF-related
if plf < 60:
    suggestions.append("⚙ PLF is low. Improve equipment utilization and reduce outages.")
if plf < 40:
    suggestions.append("🔧 PLF critically low. Conduct thorough maintenance and improve scheduling.")
if plf > 90:
    suggestions.append("🏭 High PLF. Ensure equipment is maintained to avoid forced outages.")
if plf > 100:
    suggestions.append("⚠ PLF cannot exceed 100%. Please verify input values.")

# Fuel cost
if fuel_cost > 4.0:
    suggestions.append("🔥 High fuel cost. Try renegotiating contracts or sourcing cheaper fuel.")
if fuel_cost < 2.5:
    suggestions.append("✅ Good fuel cost control. Continue efficient fuel sourcing strategies.")
if 3.0 <= fuel_cost <= 3.5:
    suggestions.append("📊 Fuel cost is moderate. Scope exists for further savings.")

# CO2 emissions
if predicted_co2 > 2000000:
    suggestions.append("🌫 Very high CO₂. Shift to cleaner fuel and increase renewable share.")
if predicted_co2 < 800000:
    suggestions.append("🌱 Low emissions. Great job integrating renewables or efficient fuel use.")
if re_share < 20 and predicted_co2 > 1000000:
    suggestions.append("🌍 Increase RE share to cut down on emissions.")

# Renewable energy share
if re_share < 20:
    suggestions.append("⚡ Renewable share is low. Increase RE capacity to cut emissions.")
if re_share > 50:
    suggestions.append("☀ High RE share! This will reduce long-term costs and pollution.")
if 25 <= re_share <= 35:
    suggestions.append("🌤 Moderate RE share. Consider gradual ramp-up.")

# Fuel availability
if coal_received < 15000000:
    suggestions.append("🪨 Coal received is low. Ensure stable coal supply chain.")
if gas_received < 2000:
    suggestions.append("⛽ Gas availability is low. Assess supply risk and backup plans.")
if gas_received > 6000:
    suggestions.append("💨 High gas input. Ensure gas turbines are utilized efficiently.")

# Installed capacity
if installed_capacity > 80000:
    suggestions.append("🏗 Large installed base. Focus on centralized efficiency upgrades.")
if installed_capacity < 20000:
    suggestions.append("🔌 Small capacity plant. Consider expansion if demand rises.")

# Power output
if predicted_power < 100:
    suggestions.append("📉 Power output very low. Check input fuel and PLF settings.")
if predicted_power > 800:
    suggestions.append("📈 Excellent generation capacity utilization!")

# Tariff
if avg_tariff < 3.0:
    suggestions.append("💵 Tariff too low. Try negotiating higher tariffs to improve margins.")
if avg_tariff > 5.0:
    suggestions.append("💸 High tariff. Be cautious as customers may push back.")
if 3.5 <= avg_tariff <= 4.5:
    suggestions.append("✅ Reasonable tariff range.")

# Balanced cases
if fuel_cost > 3.5 and avg_tariff < 3.5:
    suggestions.append("🧮 Margins tight. Fuel cost is high, but tariff is low. Not sustainable.")
if profit > 5000 and re_share > 30 and predicted_co2 < 1000000:
    suggestions.append("🌟 Excellent performance: High profit, good RE share, and low emissions.")
if plf > 85 and fuel_cost < 3.0:
    suggestions.append("⚡ Very efficient operation: High PLF and low cost per unit.")

# General guidance
suggestions.append("📘 Tip: Keep PLF above 75% to ensure efficient operation.")
suggestions.append("📘 Tip: Increase RE share to reduce carbon emissions and fuel cost.")
suggestions.append("📘 Tip: Regular maintenance can improve PLF and reduce forced outages.")
suggestions.append("📘 Tip: Keep monitoring coal and gas supply to avoid disruptions.")
suggestions.append("📘 Tip: Use AI and analytics to optimize load distribution across units.")

# Show suggestions
shown_suggestions = set()
for s in suggestions:
    if len(shown_suggestions) < 50 and s not in shown_suggestions:
        st.info(s)
        shown_suggestions.add(s)

if not shown_suggestions:
    st.success("✅ All performance indicators look good! Keep it up.")

# Show past predictions and download option
if st.session_state.all_predictions:
    st.markdown("### 🗃 All Predictions This Session")
    all_df = pd.concat(st.session_state.all_predictions, ignore_index=True)
    st.dataframe(all_df)

    csv_all = all_df.to_csv(index=False)

    st.download_button(
        label="📥 Download All Predictions as CSV",
        data=csv_all,
        file_name="all_ntpc_predictions.csv",
        mime="text/csv"
    )
    
import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("ntpc_model.pkl")

# Maintain session history
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

# Profit-related
if profit < 1000:
    suggestions.append("📉 Profit is low. Try increasing average tariff or improving operational efficiency.")
if profit < 0:
    suggestions.append("🔴 Negative profit. Review your fuel cost and increase tariff if possible.")
if revenue < 1000:
    suggestions.append("💸 Low revenue. Consider boosting generation or negotiating higher tariffs.")
if revenue > 10000:
    suggestions.append("💰 Excellent revenue! Keep monitoring costs to maintain high profit.")
if cost > 9000:
    suggestions.append("💡 Fuel cost is very high. Try optimizing fuel mix or increasing efficiency.")

# PLF-related
if plf < 60:
    suggestions.append("⚙ PLF is low. Improve equipment utilization and reduce outages.")
if plf < 40:
    suggestions.append("🔧 PLF critically low. Conduct thorough maintenance and improve scheduling.")
if plf > 90:
    suggestions.append("🏭 High PLF. Ensure equipment is maintained to avoid forced outages.")
if plf > 100:
    suggestions.append("⚠ PLF cannot exceed 100%. Please verify input values.")

# Fuel cost
if fuel_cost > 4.0:
    suggestions.append("🔥 High fuel cost. Try renegotiating contracts or sourcing cheaper fuel.")
if fuel_cost < 2.5:
    suggestions.append("✅ Good fuel cost control. Continue efficient fuel sourcing strategies.")
if 3.0 <= fuel_cost <= 3.5:
    suggestions.append("📊 Fuel cost is moderate. Scope exists for further savings.")

# CO2 emissions
if predicted_co2 > 2000000:
    suggestions.append("🌫 Very high CO₂. Shift to cleaner fuel and increase renewable share.")
if predicted_co2 < 800000:
    suggestions.append("🌱 Low emissions. Great job integrating renewables or efficient fuel use.")
if re_share < 20 and predicted_co2 > 1000000:
    suggestions.append("🌍 Increase RE share to cut down on emissions.")

# Renewable energy share
if re_share < 20:
    suggestions.append("⚡ Renewable share is low. Increase RE capacity to cut emissions.")
if re_share > 50:
    suggestions.append("☀ High RE share! This will reduce long-term costs and pollution.")
if 25 <= re_share <= 35:
    suggestions.append("🌤 Moderate RE share. Consider gradual ramp-up.")

# Fuel availability
if coal_received < 15000000:
    suggestions.append("🪨 Coal received is low. Ensure stable coal supply chain.")
if gas_received < 2000:
    suggestions.append("⛽ Gas availability is low. Assess supply risk and backup plans.")
if gas_received > 6000:
    suggestions.append("💨 High gas input. Ensure gas turbines are utilized efficiently.")

# Installed capacity
if installed_capacity > 80000:
    suggestions.append("🏗 Large installed base. Focus on centralized efficiency upgrades.")
if installed_capacity < 20000:
    suggestions.append("🔌 Small capacity plant. Consider expansion if demand rises.")

# Power output
if predicted_power < 100:
    suggestions.append("📉 Power output very low. Check input fuel and PLF settings.")
if predicted_power > 800:
    suggestions.append("📈 Excellent generation capacity utilization!")

# Tariff
if avg_tariff < 3.0:
    suggestions.append("💵 Tariff too low. Try negotiating higher tariffs to improve margins.")
if avg_tariff > 5.0:
    suggestions.append("💸 High tariff. Be cautious as customers may push back.")
if 3.5 <= avg_tariff <= 4.5:
    suggestions.append("✅ Reasonable tariff range.")

# Balanced cases
if fuel_cost > 3.5 and avg_tariff < 3.5:
    suggestions.append("🧮 Margins tight. Fuel cost is high, but tariff is low. Not sustainable.")
if profit > 5000 and re_share > 30 and predicted_co2 < 1000000:
    suggestions.append("🌟 Excellent performance: High profit, good RE share, and low emissions.")
if plf > 85 and fuel_cost < 3.0:
    suggestions.append("⚡ Very efficient operation: High PLF and low cost per unit.")

# General guidance
suggestions.append("📘 Tip: Keep PLF above 75% to ensure efficient operation.")
suggestions.append("📘 Tip: Increase RE share to reduce carbon emissions and fuel cost.")
suggestions.append("📘 Tip: Regular maintenance can improve PLF and reduce forced outages.")
suggestions.append("📘 Tip: Keep monitoring coal and gas supply to avoid disruptions.")
suggestions.append("📘 Tip: Use AI and analytics to optimize load distribution across units.")

# Show suggestions
shown_suggestions = set()
for s in suggestions:
    if len(shown_suggestions) < 50 and s not in shown_suggestions:
        st.info(s)
        shown_suggestions.add(s)

if not shown_suggestions:
    st.success("✅ All performance indicators look good! Keep it up.")

# Show past predictions and download option
if st.session_state.all_predictions:
    st.markdown("### 🗃 All Predictions This Session")
    all_df = pd.concat(st.session_state.all_predictions, ignore_index=True)
    st.dataframe(all_df)

    csv_all = all_df.to_csv(index=False)

    st.download_button(
        label="📥 Download All Predictions as CSV",
        data=csv_all,
        file_name="all_ntpc_predictions.csv",
        mime="text/csv"
    )
