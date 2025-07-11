
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from helpers import generate_summary, get_recommendations, calculate_savings_rate
from auth import login, is_logged_in

st.set_page_config(page_title="Advanced Personal Finance Advisor", layout="wide")

# Logo and title
st.image("assets/logo.png", width=80)
st.title("💰 Advanced Personal Finance Advisor")

# User Authentication
if not is_logged_in():
    login()
    st.stop()

# Upload or use sample
uploaded_file = st.file_uploader("📁 Upload your CSV (Income/Expense data)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/sample_data.csv")
    st.info("Using sample data")

df["Date"] = pd.to_datetime(df["Date"])

# Show raw data
st.subheader("🧾 Transaction Data")
st.dataframe(df)

# Monthly selector
df["Month"] = df["Date"].dt.to_period("M").astype(str)
month = st.selectbox("📆 Select Month", df["Month"].unique())
month_df = df[df["Month"] == month]

# Summary and savings rate
summary = generate_summary(month_df)
savings_rate = calculate_savings_rate(summary["Total Income"], summary["Net Savings"])
summary["Savings Rate (%)"] = savings_rate
st.subheader("📊 Monthly Summary")
st.json(summary)

# Visualization
st.subheader("📈 Expense Distribution")
expense_data = month_df[month_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
fig, ax = plt.subplots()
expense_data.plot.pie(autopct='%1.1f%%', ax=ax)
ax.set_ylabel('')
st.pyplot(fig)

# Recommendations
st.subheader("💡 Recommendations")
for rec in get_recommendations(summary):
    st.markdown(f"- {rec}")
