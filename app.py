import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Load model
model = joblib.load("ntpc_model.pkl")

st.set_page_config(page_title="NTPC Predictor", layout="wide")
st.title("NTPC Power & CO₂ Predictor")
st.markdown("Predict power generation, CO₂ emissions, revenue, fuel cost, and profit.")

# Input form
with st.form("prediction_form"):
    st.subheader("Enter Plant Parameters")
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
        email = st.text_input("Enter Email (optional)", placeholder="example@domain.com")

    submit = st.form_submit_button("Predict")

# Run prediction
if submit:
    input_df = pd.DataFrame([[installed_capacity, coal_received, gas_received, plf, fuel_cost, avg_tariff, re_share]],
                            columns=['Installed_Capacity_MW', 'Coal_Received_MTPA', 'Gas_Received_MMSCM', 'PLF_Percentage',
                                     'Fuel_Cost_per_Unit', 'Avg_Tariff (ECR)', 'RE_Share_Percentage'])

    prediction = model.predict(input_df)
    predicted_power, predicted_co2 = prediction[0]

    revenue = predicted_power * avg_tariff * 100
    cost = predicted_power * fuel_cost * 100
    profit = revenue - cost

    st.success("Prediction Complete")
    colA, colB, colC = st.columns(3)
    colA.metric("Power (BU)", f"{predicted_power:.2f}")
    colB.metric("CO₂ Emissions (Tonnes)", f"{predicted_co2:,.2f}")
    colC.metric("Profit (Cr)", f"₹{profit:,.2f}")

    # 📈 Charts
    st.subheader("Visual Analysis")
    fig, ax = plt.subplots()
    ax.bar(["Revenue", "Cost", "Profit"], [revenue, cost, profit], color=["green", "red", "blue"])
    ax.set_ylabel("₹ in Crores")
    st.pyplot(fig)

    # Suggestion system (example)
    st.subheader("Suggestions")
    suggestions = []
    if plf < 60:
        suggestions.append("PLF is low. Try increasing plant load factor for better utilization.")
    if re_share < 20:
        suggestions.append("Increase renewable energy share to reduce CO₂ emissions.")
    if fuel_cost > 4:
        suggestions.append("Fuel cost is high. Explore alternative fuel sources.")
    if predicted_power < 20:
        suggestions.append("Low power output. Improve PLF or check fuel availability.")
    if predicted_co2 > 1000000:
        suggestions.append("High CO₂ output. Use cleaner fuels or raise RE contribution.")

    for s in suggestions:
        st.warning(s)

    # 📩 Email Report
    if email:
        csv_path = "/tmp/prediction_result.csv"
        input_df['Predicted Power (BU)'] = predicted_power
        input_df['CO₂ Emissions (Tonnes)'] = predicted_co2
        input_df['Revenue (Cr)'] = revenue
        input_df['Cost (Cr)'] = cost
        input_df['Profit (Cr)'] = profit
        input_df.to_csv(csv_path, index=False)

        msg = MIMEMultipart()
        msg['From'] = os.environ["dbotchat@gmail.com"]
        msg['To'] = email
        msg['Subject'] = "NTPC Prediction Report"

        msg.attach(MIMEText("Attached is your NTPC prediction report.", "plain"))
        with open(csv_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="prediction_result.csv")
            part['Content-Disposition'] = 'attachment; filename="prediction_result.csv"'
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.environ["dbotchat@gmail.com"], os.environ["Vision@12345"])
        server.send_message(msg)
        server.quit()

        st.success("Report sent to your email.")

