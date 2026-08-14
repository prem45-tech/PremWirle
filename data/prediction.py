import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_next_week(df):

    expenses = df[
        df["transaction_type"] == "Expense"
    ].copy()

    if expenses.empty:
        return None

    expenses["date"] = pd.to_datetime(
        expenses["date"]
    )

    weekly_expenses = (
        expenses
        .groupby(
            expenses["date"].dt.to_period("W")
        )["amount"]
        .sum()
        .reset_index()
    )

    if len(weekly_expenses) < 2:
        return None

    weekly_expenses["week_number"] = range(
        1,
        len(weekly_expenses) + 1
    )

    X = weekly_expenses[
        ["week_number"]
    ]

    y = weekly_expenses[
        "amount"
    ]

    model = LinearRegression()

    model.fit(X, y)

    next_week = [
        [len(weekly_expenses) + 1]
    ]

    prediction = model.predict(
        next_week
    )[0]

    return max(0, prediction)