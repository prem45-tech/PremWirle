def calculate_summary(df):

    if df.empty:
        return 0, 0, 0, 0

    income = df[
        df["transaction_type"] == "Income"
    ]["amount"].sum()

    expenses = df[
        df["transaction_type"] == "Expense"
    ]["amount"].sum()

    balance = income - expenses

    if income > 0:
        savings_rate = (
            balance / income
        ) * 100
    else:
        savings_rate = 0

    return (
        income,
        expenses,
        balance,
        savings_rate
    )