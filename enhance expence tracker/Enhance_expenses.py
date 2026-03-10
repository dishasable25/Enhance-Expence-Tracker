import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# File to store expenses
EXPENSE_FILE = 'enhanced_expenses.csv'

# Predefined categories with emojis
CATEGORIES = {
    "1": "🍔 Food",
    "2": "🚕 Transport",
    "3": "🎮 Entertainment",
    "4": "📚 Education",
    "5": "💻 Technology",
    "6": "🏠 Rent",
    "7": "🛍 Shopping",
    "8": "💡 Utilities",
    "9": "🎁 Gifts"
}

# Load or initialize the data
def load_expenses():
    
    try:
        df = pd.read_csv(EXPENSE_FILE, names=['Date', 'Category', 'Amount'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df.dropna()
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Category', 'Amount'])

def save_expenses(df):
    df.to_csv(EXPENSE_FILE, index=False, header=False)

if 'expenses' not in st.session_state:
    st.session_state['expenses'] = load_expenses()

def add_expense(date, category, amount):
    new_expense = pd.DataFrame([[date, category, amount]], columns=['Date', 'Category', 'Amount'])
    new_expense['Date'] = pd.to_datetime(new_expense['Date'])
    st.session_state['expenses'] = pd.concat([st.session_state['expenses'], new_expense], ignore_index=True)
    save_expenses(st.session_state['expenses'])

# Styling the App
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFDEE9, #B5FFFC);
        background-size: cover;
        font-family: 'Arial', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #D8E3E7;
    }
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 50px;
        width: 200px;
        font-size: 16px;
        margin: 5px;
    }
    div.stButton > button:first-child:hover {
        background-color: #45a049;
        color: white;
    }
    .stMetric {
        background-color: #FFFBF0;
        padding: 10px;
        border-radius: 5px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🌟 Navigation")
tab = st.sidebar.radio("Select an Option:", ["Add Expense", "View Expenses", "Analyze Expenses", "Predict Expenses"])

if tab == "Add Expense":
    st.title("💰 Expense Tracker")
    st.header("➕ Add an Expense")
    date = st.date_input("Select Date", value=datetime.now().date())
    category = st.selectbox("Select Category", options=CATEGORIES.values())
    amount = st.number_input("Enter Amount (₹)", min_value=0.0, step=0.01)
    if st.button("Add Expense"):
        add_expense(date, category, amount)
        st.success(f"Expense added: {date}, {category}, ₹{amount:.2f}")

elif tab == "View Expenses":
    st.title("📄 View All Expenses")
    if not st.session_state['expenses'].empty:
        st.subheader("Your Expense Records")
        
        # Display the expenses as a table
        st.dataframe(st.session_state['expenses'])
        
        # Create a list of expense strings to display in selectbox
        expense_options = [
            f"{row['Date']} - {row['Category']} - ₹{row['Amount']:.2f}"
            for _, row in st.session_state['expenses'].iterrows()
        ]
        
        # Selectbox for deleting an expense
        expense_to_delete = st.selectbox("Select an Expense to Delete", options=expense_options)

        if st.button("Delete Selected Expense"):
            # Find the index of the selected expense in the DataFrame
            selected_index = st.session_state['expenses'][st.session_state['expenses'].apply(
                lambda row: f"{row['Date']} - {row['Category']} - ₹{row['Amount']:.2f}" == expense_to_delete, axis=1
            )].index

            if len(selected_index) > 0:
                st.session_state['expenses'] = st.session_state['expenses'].drop(selected_index)
                save_expenses(st.session_state['expenses'])
                st.success("Expense deleted successfully.")
            else:
                st.error("Expense not found.")
        
        # Selectbox for editing an expense
        expense_to_edit = st.selectbox("Select an Expense to Edit", options=expense_options)

        # Get the index of the selected expense to edit
        if expense_to_edit:
            selected_index_edit = st.session_state['expenses'][st.session_state['expenses'].apply(
                lambda row: f"{row['Date']} - {row['Category']} - ₹{row['Amount']:.2f}" == expense_to_edit, axis=1
            )].index

            if len(selected_index_edit) > 0:
                expense_to_edit_data = st.session_state['expenses'].iloc[selected_index_edit[0]]
                # Edit form
                new_date = st.date_input("New Date", value=expense_to_edit_data['Date'].date())
                new_category = st.selectbox("New Category", options=CATEGORIES.values(), index=list(CATEGORIES.values()).index(expense_to_edit_data['Category']))
                new_amount = st.number_input("New Amount (₹)", min_value=0.0, step=0.01, value=expense_to_edit_data['Amount'])
                
                if st.button("Save Changes"):
                    st.session_state['expenses'].at[selected_index_edit[0], 'Date'] = pd.to_datetime(new_date)
                    st.session_state['expenses'].at[selected_index_edit[0], 'Category'] = new_category
                    st.session_state['expenses'].at[selected_index_edit[0], 'Amount'] = new_amount
                    save_expenses(st.session_state['expenses'])
                    st.success(f"Expense updated: {new_date}, {new_category}, ₹{new_amount:.2f}")
            else:
                st.error("Expense not found for editing.")
            
    else:  
        st.info("No expenses recorded yet.")

elif tab == "Analyze Expenses":
    st.title("📊 Analyze Your Expenses")
    if not st.session_state['expenses'].empty:
        fig = px.bar(
            st.session_state['expenses'],
            x="Category",
            y="Amount",
            color="Category",
            title="📊 Category-wise Expenses",
            text="Amount",
            labels={"Amount": "Total Spent (₹)", "Category": "Expense Category"}
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(hovermode="x unified", title_font_size=20)
        st.plotly_chart(fig)
    else:
        st.info("No data available for analysis.")

elif tab == "Predict Expenses":
    st.title("🔮 Predict Future Expenses")
    if len(st.session_state['expenses']) < 2:
        st.warning("Not enough data to predict expenses.")
    else:
        st.metric("Predicted Expense for Tomorrow", "₹500")
