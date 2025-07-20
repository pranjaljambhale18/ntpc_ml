import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("ntpc_model.pkl")

# Session state to store all predictions
if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []

st.set_page_config(page_title="NTPC Predictor", layout="centered")
st.title("🔮 NTPC Power & CO₂ Predictor")
st.markdown("This app predicts power generation, CO₂ emissions, revenue, fuel cost, and profit based on your inputs.")

# --- Input Section with Default Values and Sliders ---
st.sidebar.header("📊 Input Parameters")

avg_tariff = st.sidebar.slider("📈 Average Tariff (₹/kWh)", min_value=2.0, max_value=8.0, value=4.5, step=0.1)
fuel_cost = st.sidebar.slider("🔥 Fuel Cost (₹/kWh)", min_value=1.0, max_value=5.0, value=2.8, step=0.1)
plf = st.sidebar.slider("⚙️ PLF (Plant Load Factor %)", min_value=50, max_value=100, value=75, step=1)
re_share = st.sidebar.slider("🌱 Renewable Share (%)", min_value=0, max_value=100, value=20, step=1)

# Prepare input DataFrame
input_df = pd.DataFrame([{
    "Avg_Tariff": avg_tariff,
    "Fuel_Cost": fuel_cost,
    "PLF": plf,
    "RE_Share": re_share
}])

# --- Prediction Section ---
if st.button("🚀 Predict"):
    try:
        prediction = model.predict(input_df)
        predicted_power, predicted_co2 = prediction[0]

        # Derived metrics
        revenue = predicted_power * avg_tariff * 100
        cost = predicted_power * fuel_cost * 100
        profit = revenue - cost

        # Append results to input_df
        input_df["Predicted_Power_BU"] = predicted_power
        input_df["Predicted_CO2_Tonnes"] = predicted_co2
        input_df["Revenue_Cr"] = revenue
        input_df["Fuel_Cost_Cr"] = cost
        input_df["Profit_Cr"] = profit

        # Save to session
        st.session_state.all_predictions.append(input_df)

        st.success("✅ Prediction Complete")
        st.metric("🔋 Predicted Power", f"{predicted_power:.2f} BU")
        st.metric("🌍 Predicted CO₂ Emissions", f"{predicted_co2:,.2f} Tonnes")
        st.metric("💰 Revenue", f"₹{revenue:,.2f} Cr")
        st.metric("🔥 Fuel Cost", f"₹{cost:,.2f} Cr")
        st.metric("📈 Estimated Profit", f"₹{profit:,.2f} Cr")

        # --- Suggestions ---
        st.markdown("### 💡 Suggestions Based on Your Inputs")
        suggestions = []

        if profit < 1000:
            suggestions.append("🔼 Consider increasing the average tariff or optimizing operational efficiency to boost profit.")
        if fuel_cost > 3.5:
            suggestions.append("💸 Fuel cost per unit seems high. Explore cost-effective fuel procurement or optimize plant heat rate.")
        if plf < 70:
            suggestions.append("⚙️ Low PLF. Improve plant utilization to enhance power output and reduce per-unit cost.")
        if re_share < 25:
            suggestions.append("🌿 Low RE share. Integrating more renewable energy can help reduce carbon emissions.")
        if predicted_co2 > 1000000:
            suggestions.append("🌍 High CO₂ emissions. Consider increasing RE share or improving combustion efficiency.")
        if predicted_power < 200:
            suggestions.append("🔋 Power generation is relatively low. Check fuel availability or PLF for optimization.")
        if profit < 0:
            suggestions.append("🔴 Loss-making scenario. Review tariff rates, fuel mix, and operational strategies.")

        if suggestions:
            for s in suggestions:
                st.info(s)
        else:
            st.success("✅ All performance indicators look good! Keep it up.")

        # --- Download Section ---
        st.markdown("### 📥 Download This Prediction")
        csv = input_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Prediction as CSV",
            data=csv,
            file_name="ntpc_prediction.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error in prediction: {e}")

# --- Show All Predictions ---
if st.session_state.all_predictions:
    st.markdown("### 🗃️ All Predictions This Session")
    all_df = pd.concat(st.session_state.all_predictions, ignore_index=True)
    st.dataframe(all_df)

    csv_all = all_df.to_csv(index=False)
    st.download_button(
        label="📂 Download All Predictions as CSV",
        data=csv_all,
        file_name="all_ntpc_predictions.csv",
        mime="text/csv"
    )
