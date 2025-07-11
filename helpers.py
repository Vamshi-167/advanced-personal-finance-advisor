
def generate_summary(df):
    income = df[df['Type'] == 'Income']['Amount'].sum()
    expenses = df[df['Type'] == 'Expense']['Amount'].sum()
    savings = income - expenses
    if not df[df['Type'] == 'Expense'].empty:
        top_cat = df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().idxmax()
    else:
        top_cat = "None"
    return {
        "Total Income": round(income, 2),
        "Total Expenses": round(expenses, 2),
        "Net Savings": round(savings, 2),
        "Top Expense Category": top_cat
    }

def get_recommendations(summary):
    tips = []
    if summary["Net Savings"] < 0:
        tips.append("You're spending more than you earn. Consider reducing discretionary expenses.")
    else:
        tips.append("Good job saving this month! Consider investing or emergency funds.")

    if summary["Top Expense Category"].lower() in ["food", "entertainment"]:
        tips.append(f"Spending a lot on {summary['Top Expense Category']}. Consider setting a budget limit.")

    if summary["Savings Rate (%)"] > 20:
        tips.append("Excellent savings rate! Keep it above 20% if possible.")

    return tips

def calculate_savings_rate(income, savings):
    if income == 0:
        return 0
    return round((savings / income) * 100, 2)
