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
    delete_transaction,
    get_all_users,
    get_all_transactions
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

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


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
                    st.session_state.user_email = user[2]

                    if len(user) >= 4:
                        st.session_state.is_admin = bool(
                            user[3]
                        )
                    else:
                        st.session_state.is_admin = False

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

    # SIDEBAR

    st.sidebar.title("💰 SmartSpend")

    st.sidebar.write(
        f"Welcome, **{st.session_state.user_name}** 👋"
    )

    if st.session_state.is_admin:

        st.sidebar.success(
            "👑 Administrator"
        )

    else:

        st.sidebar.info(
            "👤 User Account"
        )

    st.sidebar.divider()

    st.sidebar.title("📌 Navigation")

    navigation_pages = [
        "Dashboard",
        "Add Transaction",
        "Analytics",
        "Prediction",
        "Transaction History"
    ]

    if st.session_state.is_admin:

        navigation_pages.append(
            "👑 Admin Dashboard"
        )

    page = st.sidebar.radio(
        "Go to",
        navigation_pages
    )

    # LOGOUT

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.session_state.is_admin = False

        st.rerun()

    # LOAD CURRENT USER DATA

    df = get_transactions(
        st.session_state.user_id
    )


    # DASHBOARD

    if page == "Dashboard":

        st.title("💰 SmartSpend")

        st.subheader(
            f"Welcome back, "
            f"{st.session_state.user_name}! 👋"
        )

        st.divider()

        st.header(
            "📊 Financial Dashboard"
        )

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

        st.header(
            "➕ Add New Transaction"
        )

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

        st.header(
            "📈 Spending Analytics"
        )

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

                expense_df["week"] = (
                    expense_df["date"]
                    .dt.to_period("W")
                    .astype(str)
                )

                weekly_data = (
                    expense_df
                    .groupby("week")["amount"]
                    .sum()
                    .reset_index()
                )

                fig2 = px.line(
                    weekly_data,
                    x="week",
                    y="amount",
                    markers=True,
                    title="📅 Weekly Spending Trend"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

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

                fig3 = px.line(
                    monthly_data,
                    x="month",
                    y="amount",
                    markers=True,
                    title="📅 Monthly Spending Trend"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )


    # PREDICTION

    elif page == "Prediction":

        st.header(
            "🔮 Next Week Spending Prediction"
        )

        prediction = predict_next_week(
            df
        )

        if prediction is None:

            st.warning(
                "Add expenses from at least "
                "2 different weeks to generate "
                "a prediction."
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

        st.header(
            "📋 Transaction History"
        )

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


    # ADMIN DASHBOARD

    elif page == "👑 Admin Dashboard":

        if not st.session_state.is_admin:

            st.error(
                "🚫 Access denied."
            )

            st.stop()

        st.title(
            "👑 Admin Dashboard"
        )

        st.subheader(
            "SmartSpend System Administration"
        )

        st.divider()

        try:

            users_df = get_all_users()

            all_transactions_df = (
                get_all_transactions()
            )

        except Exception as e:

            st.error(
                "Admin database functions are not "
                "available in database.py."
            )

            st.code(
                str(e)
            )

            st.stop()

        # ADMIN SUMMARY

        total_users = len(users_df)

        if all_transactions_df.empty:

            total_income = 0
            total_expenses = 0
            total_balance = 0

        else:

            total_income = all_transactions_df[
                all_transactions_df["transaction_type"]
                == "Income"
            ]["amount"].sum()

            total_expenses = all_transactions_df[
                all_transactions_df["transaction_type"]
                == "Expense"
            ]["amount"].sum()

            total_balance = (
                total_income - total_expenses
            )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "👥 Total Users",
            total_users
        )

        col2.metric(
            "💵 Total Income",
            f"₹{total_income:,.2f}"
        )

        col3.metric(
            "💸 Total Expenses",
            f"₹{total_expenses:,.2f}"
        )

        col4.metric(
            "💰 Total Balance",
            f"₹{total_balance:,.2f}"
        )

        st.divider()

        # REGISTERED USERS

        st.header(
            "👥 Registered Users"
        )

        if users_df.empty:

            st.info(
                "No registered users found."
            )

        else:

            st.dataframe(
                users_df,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # ALL TRANSACTIONS

        st.header(
            "📋 All User Transactions"
        )

        if all_transactions_df.empty:

            st.info(
                "No transactions found."
            )

        else:

            admin_df = all_transactions_df.copy()

            if "user_name" in admin_df.columns:

                user_options = [
                    "All Users"
                ] + sorted(
                    admin_df["user_name"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_user = st.selectbox(
                    "👤 Filter by User",
                    user_options
                )

                if selected_user != "All Users":

                    admin_df = admin_df[
                        admin_df["user_name"]
                        == selected_user
                    ]

            if "date" in admin_df.columns:

                admin_df["date"] = pd.to_datetime(
                    admin_df["date"],
                    errors="coerce"
                )

                valid_dates = admin_df[
                    admin_df["date"].notna()
                ]["date"]

                if not valid_dates.empty:

                    min_date = (
                        valid_dates.min().date()
                    )

                    max_date = (
                        valid_dates.max().date()
                    )

                    date_range = st.date_input(
                        "📅 Filter by Date",
                        value=(
                            min_date,
                            max_date
                        ),
                        min_value=min_date,
                        max_value=max_date
                    )

                    if len(date_range) == 2:

                        start_date = pd.Timestamp(
                            date_range[0]
                        )

                        end_date = (
                            pd.Timestamp(
                                date_range[1]
                            )
                            + pd.Timedelta(days=1)
                        )

                        admin_df = admin_df[
                            (
                                admin_df["date"]
                                >= start_date
                            )
                            &
                            (
                                admin_df["date"]
                                < end_date
                            )
                        ]

            st.dataframe(
                admin_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                label="📥 Download All Transaction Data",
                data=admin_df.to_csv(
                    index=False
                ),
                file_name=(
                    "smartspend_admin_transactions.csv"
                ),
                mime="text/csv"
            )

        st.divider()

        # USER-WISE EXPENSES

        if not all_transactions_df.empty:

            st.header(
                "📊 User-wise Expenses"
            )

            if "user_name" in all_transactions_df.columns:

                expense_admin_df = (
                    all_transactions_df[
                        all_transactions_df[
                            "transaction_type"
                        ] == "Expense"
                    ]
                )

                if not expense_admin_df.empty:

                    user_expenses = (
                        expense_admin_df
                        .groupby("user_name")[
                            "amount"
                        ]
                        .sum()
                        .reset_index()
                        .sort_values(
                            "amount",
                            ascending=False
                        )
                    )

                    fig_admin = px.bar(
                        user_expenses,
                        x="user_name",
                        y="amount",
                        title="💸 Total Expenses by User"
                    )

                    st.plotly_chart(
                        fig_admin,
                        use_container_width=True
                    )

        # CATEGORY ANALYSIS

        if not all_transactions_df.empty:

            expense_admin_df = (
                all_transactions_df[
                    all_transactions_df[
                        "transaction_type"
                    ] == "Expense"
                ]
            )

            if not expense_admin_df.empty:

                st.header(
                    "📊 Overall Spending by Category"
                )

                category_admin = (
                    expense_admin_df
                    .groupby("category")[
                        "amount"
                    ]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "amount",
                        ascending=False
                    )
                )

                fig_category = px.pie(
                    category_admin,
                    names="category",
                    values="amount",
                    title="💸 Overall Spending by Category"
                )

                st.plotly_chart(
                    fig_category,
                    use_container_width=True
                )


    # USER CSV DOWNLOAD

    if not df.empty:

        st.sidebar.divider()

        st.sidebar.download_button(
            label="📥 Download My Transactions",
            data=df.to_csv(
                index=False
            ),
            file_name="smartspend_transactions.csv",
            mime="text/csv"
        )