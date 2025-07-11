
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from helpers import generate_summary, get_recommendations, calculate_savings_rate
from auth import login, is_logged_in

st.set_page_config(page_title="Advanced Personal Finance Advisor", layout="wide")

# Logo and title
st.image("assets/logo.png", width=80)
st.title("💰 Advanced Personal Finance Advisor")

# Session init
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not is_logged_in():
    login()
    st.stop()

# Read latest data
df = pd.read_csv("data/sample_data.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# ---------------------- Data Entry Form ----------------------
st.subheader("➕ Add a New Transaction")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date")
        t_type = st.selectbox("Type", ["Income", "Expense"])
    with col2:
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        category = st.text_input("Category")

    submitted = st.form_submit_button("Save Entry")

    if submitted:
        new_data = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"),
            "Type": t_type,
            "Amount": amount,
            "Category": category
        }])
        new_data.to_csv("data/sample_data.csv", mode='a', header=False, index=False)
        st.success("✅ Transaction added!")
        st.experimental_rerun()  # Force refresh with new data

# ---------------------- Dashboard ----------------------
st.subheader("📅 Select a Month")
month = st.selectbox("Month", df["Month"].unique())
month_df = df[df["Month"] == month]

# Show raw data
st.subheader("🧾 Transactions")
st.dataframe(month_df)

# Summary and savings rate
summary = generate_summary(month_df)
savings_rate = calculate_savings_rate(summary["Total Income"], summary["Net Savings"])
summary["Savings Rate (%)"] = savings_rate
st.subheader("📊 Monthly Summary")
st.json(summary)

# Pie chart
st.subheader("📈 Expense Distribution")
expense_data = month_df[month_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
fig, ax = plt.subplots()
if not expense_data.empty:
    expense_data.plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)
else:
    st.write("No expense data for this month.")

# Recommendations
st.subheader("💡 Recommendations")
for rec in get_recommendations(summary):
    st.markdown(f"- {rec}")
