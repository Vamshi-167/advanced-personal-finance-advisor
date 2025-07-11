
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from helpers import generate_summary, get_recommendations, calculate_savings_rate
from auth import login, is_logged_in

st.set_page_config(page_title="Advanced Personal Finance Advisor", layout="wide")
st.image("assets/logo.png", width=80)
st.title("💰 Advanced Personal Finance Advisor")

if "auth" not in st.session_state:
    st.session_state["auth"] = False
if not is_logged_in():
    login()
    st.stop()

# Load and preprocess data
df = pd.read_csv("data/sample_data.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Add new transaction
st.subheader("➕ Add New Transaction")
with st.form("add_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_date = st.date_input("Date")
        new_type = st.selectbox("Type", ["Income", "Expense"])
    with col2:
        new_amount = st.number_input("Amount", min_value=0.0, step=0.01)
        new_category = st.text_input("Category")
    submitted = st.form_submit_button("Add")
    if submitted:
        new_entry = pd.DataFrame([{
            "Date": new_date.strftime("%Y-%m-%d"),
            "Type": new_type,
            "Amount": new_amount,
            "Category": new_category
        }])
        new_entry.to_csv("data/sample_data.csv", mode='a', header=False, index=False)
        st.success("✅ Entry added!")
        st.experimental_rerun()

# Edit/Delete section
st.subheader("✏️ Edit or Delete Transaction")
df["Label"] = df.apply(lambda row: f"{row['Date'].date()} | {row['Type']} | {row['Amount']} | {row['Category']}", axis=1)
selection = st.selectbox("Select transaction:", df["Label"].tolist())
selected_index = df[df["Label"] == selection].index[0]
selected_row = df.loc[selected_index]

with st.form("edit_form"):
    col1, col2 = st.columns(2)
    with col1:
        edit_date = st.date_input("Edit Date", value=selected_row["Date"])
        edit_type = st.selectbox("Edit Type", ["Income", "Expense"], index=0 if selected_row["Type"] == "Income" else 1)
    with col2:
        edit_amount = st.number_input("Edit Amount", min_value=0.0, step=0.01, value=float(selected_row["Amount"]))
        edit_category = st.text_input("Edit Category", value=selected_row["Category"])
    update_btn = st.form_submit_button("Update")
    delete_btn = st.form_submit_button("Delete")

    if update_btn:
        df.at[selected_index, "Date"] = edit_date
        df.at[selected_index, "Type"] = edit_type
        df.at[selected_index, "Amount"] = edit_amount
        df.at[selected_index, "Category"] = edit_category
        df.drop(columns=["Label"], inplace=True)
        df.to_csv("data/sample_data.csv", index=False)
        st.success("✅ Transaction updated!")
        st.experimental_rerun()

    if delete_btn:
        df.drop(index=selected_index, inplace=True)
        df.drop(columns=["Label"], inplace=True)
        df.to_csv("data/sample_data.csv", index=False)
        st.success("🗑️ Transaction deleted!")
        st.experimental_rerun()

# Dashboard
st.subheader("📅 Select a Month")
month = st.selectbox("Month", df["Month"].unique())
month_df = df[df["Month"] == month]

st.subheader("🧾 Transactions")
st.dataframe(month_df)

summary = generate_summary(month_df)
summary["Savings Rate (%)"] = calculate_savings_rate(summary["Total Income"], summary["Net Savings"])
st.subheader("📊 Monthly Summary")
st.json(summary)

# Pie Chart
st.subheader("📈 Expense Distribution")
expense_data = month_df[month_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
fig, ax = plt.subplots()
if not expense_data.empty:
    expense_data.plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)
else:
    st.write("No expense data for this month.")

st.subheader("💡 Recommendations")
for rec in get_recommendations(summary):
    st.markdown(f"- {rec}")

# Monthly trendline chart
st.subheader("📊 Monthly Trendline")
trend = df.groupby("Month").agg({
    "Amount": "sum",
    "Type": lambda x: list(x)
}).reset_index()

trend["Income"] = [sum(a for a, t in zip(df[df["Month"] == m]["Amount"], df[df["Month"] == m]["Type"]) if t == "Income") for m in trend["Month"]]
trend["Expense"] = [sum(a for a, t in zip(df[df["Month"] == m]["Amount"], df[df["Month"] == m]["Type"]) if t == "Expense") for m in trend["Month"]]
trend["Savings"] = trend["Income"] - trend["Expense"]

trend_fig, trend_ax = plt.subplots()
trend_ax.plot(trend["Month"], trend["Income"], label="Income", marker="o")
trend_ax.plot(trend["Month"], trend["Expense"], label="Expenses", marker="o")
trend_ax.plot(trend["Month"], trend["Savings"], label="Savings", marker="o")
trend_ax.set_ylabel("Amount")
trend_ax.set_xlabel("Month")
trend_ax.set_title("Monthly Financial Trend")
trend_ax.legend()
trend_ax.grid(True)
st.pyplot(trend_fig)
