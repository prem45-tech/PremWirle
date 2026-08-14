import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    create_database,
    register_user,
    login_user,
    add_transaction,
    get_transactions,
    delete_transaction
)

from analytics import calculate_summary
from prediction import predict_next_week



# PAGE CONFIGURATION


st.set_page_config(
    page_title="SmartSpend",
    page_icon="💰",
    layout="wide"
)



# INITIALIZE DATABASE


create_database()



# SESSION STATE


if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "user_id" not in st.session_state:

    st.session_state.user_id = None

if "user_name" not in st.session_state:

    st.session_state.user_name = None



# LOGIN / SIGNUP PAGE


if not st.session_state.logged_in:

    st.title("💰 SmartSpend")

    st.subheader(
        "Personal Finance & Expense Analytics"
    )

    st.divider()

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )


    # LOGIN

    with login_tab:

        st.header("Welcome Back 👋")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter email and password."
                )

            else:

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True

                    st.session_state.user_id = user[0]

                    st.session_state.user_name = user[1]

                    st.success(
                        "Login successful! 🎉"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )


    # SIGNUP

    with signup_tab:

        st.header("Create Your Account 📝")

        name = st.text_input(
            "Name",
            key="signup_name"
        )

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not name or not email or not password:

                st.error(
                    "Please fill all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Account created successfully! "
                        "You can now login. ✅"
                    )

                else:

                    st.error(
                        "An account with this email already exists."
                    )



# MAIN APPLICATION


else:

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    st.sidebar.title("💰 SmartSpend")

    st.sidebar.write(
        f"Welcome, **{st.session_state.user_name}** 👋"
    )

    st.sidebar.divider()

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

    st.sidebar.divider()

    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_id = None

        st.session_state.user_name = None

        st.rerun()


    # -----------------------------------------------------
    # LOAD ONLY CURRENT USER DATA
    # -----------------------------------------------------

    df = get_transactions(
        st.session_state.user_id
    )


    # DASHBOARD

    if page == "Dashboard":

        st.title("💰 SmartSpend")

        st.subheader(
            f"Welcome back, {st.session_state.user_name}! 👋"
        )

        st.divider()

        st.header("📊 Financial Dashboard")

        income, expenses, balance, savings_rate = (
            calculate_summary(df)
        )

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
                "No transactions yet. "
                "Add your first transaction!"
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

        with st.form(
            "transaction_form"
        ):

            transaction_type = st.selectbox(
                "Transaction Type",
                [
                    "Income",
                    "Expense"
                ]
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
                    "Pocket Money",
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
                        st.session_state.user_id,
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

                # Monthly spending

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

        st.header(
            "🔮 Next Week Spending Prediction"
        )

        prediction = predict_next_week(df)

        if prediction is None:

            st.warning(
                "Add expenses from at least 2 "
                "different weeks to generate a prediction."
            )

        else:

            st.success(
                f"Estimated next week spending: "
                f"₹{prediction:,.2f}"
            )

            st.info(
                "This prediction is based on your "
                "previous weekly spending patterns."
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
                    transaction_id,
                    st.session_state.user_id
                )

                st.success(
                    "Transaction deleted successfully."
                )

                st.rerun()


    # CSV DOWNLOAD

    if not df.empty:

        st.sidebar.download_button(
            label="📥 Download My Transactions",
            data=df.to_csv(
                index=False
            ),
            file_name=(
                "smartspend_transactions.csv"
            ),
            mime="text/csv"
        )