import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_next_month(df):

    expenses = df[
        df["transaction_type"] == "Expense"
    ].copy()

    if expenses.empty:
        return None

    expenses["date"] = pd.to_datetime(expenses["date"])

    monthly_expenses = (
        expenses
        .groupby(expenses["date"].dt.to_period("M"))["amount"]
        .sum()
        .reset_index()
    )

    if len(monthly_expenses) < 2:
        return None

    monthly_expenses["month_number"] = range(
        1,
        len(monthly_expenses) + 1
    )

    X = monthly_expenses[["month_number"]]

    y = monthly_expenses["amount"]

    model = LinearRegression()

    model.fit(X, y)

    next_month = [[len(monthly_expenses) + 1]]

    prediction = model.predict(next_month)[0]

    return max(0, prediction)