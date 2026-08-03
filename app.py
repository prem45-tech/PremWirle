import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    create_database,
    add_transaction,
    get_transactions,
    delete_transaction
)

from analytics import calculate_summary
from prediction import predict_next_month


# PAGE CONFIGURATION

st.set_page_config(
    page_title="SmartSpend",
    page_icon="💰",
    layout="wide"
)


# INITIALIZE DATABASE

create_database()


# TITLE

st.title("💰 SmartSpend")

st.subheader(
    "Personal Finance & Expense Analytics Dashboard"
)

st.divider()


# SIDEBAR

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Add Transaction",
        "Analytics",
        "Prediction",
        "Transaction History"
    ]
)


# LOAD DATA

df = get_transactions()


# DASHBOARD

if page == "Dashboard":

    st.header("📊 Financial Dashboard")

    income, expenses, balance, savings_rate = \
        calculate_summary(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💵 Total Income",
        f"₹{income:,.2f}"
    )

    col2.metric(
        "💸 Total Expenses",
        f"₹{expenses:,.2f}"
    )

    col3.metric(
        "💰 Current Balance",
        f"₹{balance:,.2f}"
    )

    col4.metric(
        "📈 Savings Rate",
        f"{savings_rate:.2f}%"
    )

    st.divider()

    if df.empty:

        st.info(
            "No transactions yet. Add your first transaction!"
        )

    else:

        expense_df = df[
            df["transaction_type"] == "Expense"
        ]

        if not expense_df.empty:

            category_data = (
                expense_df
                .groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                title="💸 Spending by Category"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ADD TRANSACTION

elif page == "Add Transaction":

    st.header("➕ Add New Transaction")

    with st.form("transaction_form"):

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Income", "Expense"]
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Salary",
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Bills",
                "Entertainment",
                "Healthcare",
                "Pocket Money"
                "Other"
            ]
        )

        transaction_date = st.date_input(
            "Date",
            date.today()
        )

        description = st.text_input(
            "Description"
        )

        submitted = st.form_submit_button(
            "Add Transaction"
        )

        if submitted:

            if amount <= 0:

                st.error(
                    "Amount must be greater than zero."
                )

            else:

                add_transaction(
                    transaction_type,
                    amount,
                    category,
                    str(transaction_date),
                    description
                )

                st.success(
                    "Transaction added successfully! ✅"
                )


# ANALYTICS

elif page == "Analytics":

    st.header("📈 Spending Analytics")

    if df.empty:

        st.warning(
            "Add transactions to view analytics."
        )

    else:

        expense_df = df[
            df["transaction_type"] == "Expense"
        ].copy()

        if expense_df.empty:

            st.info(
                "No expenses available for analysis."
            )

        else:

            expense_df["date"] = pd.to_datetime(
                expense_df["date"]
            )

            # Category chart

            category_data = (
                expense_df
                .groupby("category")["amount"]
                .sum()
                .reset_index()
                .sort_values(
                    "amount",
                    ascending=False
                )
            )

            fig1 = px.bar(
                category_data,
                x="category",
                y="amount",
                title="💸 Expenses by Category"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            # Monthly chart

            expense_df["month"] = (
                expense_df["date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_data = (
                expense_df
                .groupby("month")["amount"]
                .sum()
                .reset_index()
            )

            fig2 = px.line(
                monthly_data,
                x="month",
                y="amount",
                markers=True,
                title="📅 Monthly Spending Trend"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )


# PREDICTION

elif page == "Prediction":

    st.header("🔮 Future Spending Prediction")

    prediction = predict_next_month(df)

    if prediction is None:

        st.warning(
            "Add expenses from at least 2 different months "
            "to generate a prediction."
        )

    else:

        st.success(
            f"Estimated next month spending: "
            f"₹{prediction:,.2f}"
        )

        st.info(
            "This prediction is based on your previous "
            "monthly spending patterns."
        )


# TRANSACTION HISTORY

elif page == "Transaction History":

    st.header("📋 Transaction History")

    if df.empty:

        st.info(
            "No transactions found."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🗑️ Delete Transaction"
        )

        transaction_id = st.number_input(
            "Enter Transaction ID",
            min_value=1,
            step=1
        )

        if st.button(
            "Delete Transaction"
        ):

            delete_transaction(
                transaction_id
            )

            st.success(
                "Transaction deleted successfully."
            )

            st.rerun()


# CSV DOWNLOAD

if not df.empty:

    st.sidebar.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False),
        file_name="smartspend_transactions.csv",
        mime="text/csv"
    )