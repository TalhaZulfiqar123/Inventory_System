import streamlit as st
import pandas as pd
import os
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter

# ---------- PAGE CONFIG & LIGHT MODERN STYLE ----------
st.set_page_config(
    page_title="Smart Inventory Management",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background: #f9fafe;
        color: #1a237e;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #0d47a1;
    }
    h1, h2, h3, h4 {
        color: #1565c0 !important;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #42a5f5 0%, #66bb6a 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6em 1.5em;
        font-weight: 700;
        box-shadow: 0 2px 8px #90caf9aa;
        transition: background 0.2s, transform 0.1s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #66bb6a 0%, #42a5f5 100%);
        color: #fff;
        transform: scale(1.04);
    }
    .stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div>input {
        background: #e3f2fd;
        border-radius: 6px;
        border: 1px solid #90caf9;
        color: #1a237e;
        font-weight: 500;
    }
    .stDataFrame {
        background: #fff;
        border-radius: 12px;
        padding: 0.5em;
        box-shadow: 0 2px 12px #90caf933;
        color: #1a237e;
    }
    .stAlert {
        border-radius: 10px;
        font-weight: 600;
    }
    ::-webkit-scrollbar-thumb {
        background: #42a5f5;
        border-radius: 6px;
    }
    ::-webkit-scrollbar {
        background: #e3f2fd;
        width: 8px;
    }
    td[style*="background-color: #ffe5e5"] {
        background-color: #ef5350 !important;
        color: #fff !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- CONFIG ----------
STOCK_FILE = "stock.csv"
ASSIGNMENT_FILE = "assignments.csv"
BARCODE_FOLDER = "barcodes"
USERS = {"admin": "admin123", "staff": "staff123"}

os.makedirs(BARCODE_FOLDER, exist_ok=True)

# ---------- DATA FUNCTIONS ----------
def load_data():
    if os.path.exists(STOCK_FILE):
        df = pd.read_csv(STOCK_FILE)
        for col in ["company", "category"]:
            if col not in df.columns:
                df[col] = ""
        df['low_stock'] = df['quantity'] < 5
        return df
    return pd.DataFrame(columns=["id", "name", "company", "category", "quantity", "price", "barcode", "low_stock"])

def save_data(df):
    df.to_csv(STOCK_FILE, index=False)

def load_assignments():
    cols = ["user", "role", "stock_id", "stock_name", "date", "remarks", "status", "teacher_id", "department", "return_date"]
    if os.path.exists(ASSIGNMENT_FILE):
        df = pd.read_csv(ASSIGNMENT_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_assignments(df):
    df.to_csv(ASSIGNMENT_FILE, index=False)

def generate_barcode(uid):
    barcode_path = os.path.join(BARCODE_FOLDER, f"{uid}.png")
    Code128(uid, writer=ImageWriter()).write(open(barcode_path, 'wb'))
    return barcode_path

# ---------- LOGIN ----------
def login():
    st.sidebar.image("https://img.icons8.com/color/96/box.png", width=80)
    st.sidebar.markdown("### <span style='color:#1565c0;'>Smart Inventory</span>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🔐 Login to Inventory System</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", help="Click to login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

# ---------- PAGE FUNCTIONS ----------
def highlight_low_stock(s):
    return ['background-color: #ffe5e5' if v else '' for v in s]

def add_stock():
    st.markdown("""
        <div style='text-align:center;'>
            <span style='font-size:3rem;'>➕</span>
            <h1 style='display:inline; color:#1565c0; font-weight:800;'>Add New Stock</h1>
        </div>
        <div style='color:#1976d2; text-align:center; font-size:1.1em; margin-bottom:2em;'>
            Fill in the details to add a new product to your inventory.
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        product_code = st.text_input("Product Code (Stock ID)", placeholder="e.g. LAP12345")
        name = st.text_input("Product Name", placeholder="e.g. HP Laptop")
        company = st.selectbox("Company", ["Select...", "HP", "Dell", "Apple", "Lenovo", "Samsung", "Other"])
        if company == "Other":
            company = st.text_input("Enter Company Name")
        category = st.selectbox("Category", ["Select...", "Laptop", "Monitor", "Printer", "Accessory", "Furniture", "Other"])
        if category == "Other":
            category = st.text_input("Enter Category")
    with col2:
        price = st.number_input("Price", min_value=0.0, step=0.01)
        quantity = st.number_input("Quantity", min_value=1, value=1)
        st.markdown("<br>", unsafe_allow_html=True)
        add_btn = st.button("Add Stock", use_container_width=True)

    if add_btn:
        if not product_code or not name or company in ["Select...", ""] or category in ["Select...", ""]:
            st.warning("Please fill out all required fields.")
            return
        df = load_data()
        # Check for duplicate Product Code
        if product_code in df['id'].values:
            st.error("❌ This Product Code/Stock ID already exists. Please use a unique code.")
            return
        barcode_path = generate_barcode(product_code)
        new_row = {
            "id": product_code,
            "name": name,
            "company": company,
            "category": category,
            "quantity": quantity,
            "price": price,
            "barcode": barcode_path,
            "low_stock": quantity < 5
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success(f"✅ Stock added: {name} ({company}, {category}) - ID: {product_code}")
        if os.path.exists(barcode_path):
            st.image(barcode_path, width=180)

def manage_stock():
    st.title("🛠 Manage Stock")
    df = load_data()
    if df.empty:
        st.warning("No stock available.")
        return
    product_name = st.selectbox("Select Product Name to Manage", df['name'].tolist())
    stock = df[df['name'] == product_name]
    selected_id = st.selectbox("Select Stock ID", stock['id'].tolist())
    quantity = st.number_input("New Quantity", min_value=0, value=int(stock[stock['id']==selected_id]['quantity'].values[0]))
    price = st.number_input("New Price", min_value=0.0, step=0.01, value=float(stock[stock['id']==selected_id]['price'].values[0]))
    action = st.radio("Action", ["Update", "Delete"])
    if st.button(f"{action} Stock"):
        if action == "Update":
            df.loc[df['id'] == selected_id, 'quantity'] = quantity
            df.loc[df['id'] == selected_id, 'price'] = price
            save_data(df)
            st.success(f"Stock Updated: {product_name} (ID: {selected_id})")
        elif action == "Delete":
            df = df[df['id'] != selected_id]
            save_data(df)
            st.success(f"Stock Deleted: {product_name} (ID: {selected_id})")

def view_stock():
    st.title("🔍 View Stock")
    df = load_data()
    if df.empty:
        st.warning("No stock available.")
        return
    styled_df = df[["id", "name", "company", "category", "quantity", "price", "low_stock"]].style.apply(highlight_low_stock, subset=['low_stock'])
    st.dataframe(styled_df, use_container_width=True)
    product_name = st.selectbox("Select Product Name to View", df['name'].tolist())
    stock = df[df['name'] == product_name]
    if not stock.empty:
        selected_id = st.selectbox("Select Stock ID", stock['id'].tolist())
        product = stock[stock['id'] == selected_id].iloc[0]
        st.write(f"**Product Name**: {product['name']}")
        st.write(f"**Company**: {product['company']}")
        st.write(f"**Category**: {product['category']}")
        st.write(f"**Quantity**: {product['quantity']}")
        st.write(f"**Price**: {product['price']}")
        st.image(product['barcode'], width=200)

def assign_product():
    st.title("👥 Assign/Return Product")
    df = load_data()
    if df.empty:
        st.warning("No stock available.")
        return
    assign_df = load_assignments()
    action = st.radio("Action", ["Assign", "Return"])
    if action == "Return":
        product_id = st.text_input("Enter Stock ID to Return")
        stock = df[df['id'] == product_id]
        if not stock.empty:
            product = stock.iloc[0]
            st.write(f"**Product Name**: {product['name']}")
            st.write(f"**Quantity**: {product['quantity']}")
            st.image(product['barcode'], width=200)
            mask = (assign_df['stock_id'] == product_id) & (assign_df['status'] == "Assigned")
            if assign_df[mask].empty:
                st.warning("No outstanding assignment found for this stock ID.")
                return
            latest_idx = assign_df[mask].index[-1]
            if st.button("Return Product"):
                assign_df.at[latest_idx, 'status'] = "Returned"
                assign_df.at[latest_idx, 'return_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                df.loc[df['id'] == product_id, 'quantity'] += 1
                save_data(df)
                save_assignments(assign_df)
                st.success("Product returned successfully.")
        else:
            st.warning("Stock ID not found.")
    else:
        product_name = st.selectbox("Select Product Name", df['name'].tolist())
        stock = df[df['name'] == product_name]
        selected_id = st.selectbox("Select Stock ID", stock['id'].tolist())
        user = st.text_input("Enter User Name:")
        role = st.selectbox("Select Role", ["Teacher", "Student"])
        teacher_id = department = ""
        if role == "Teacher":
            teacher_id = st.text_input("Teacher ID")
            department = st.text_input("Department")
        remarks = st.text_area("Remarks")
        if st.button("Assign Product"):
            current_qty = stock[stock['id'] == selected_id]['quantity'].values[0]
            if current_qty <= 0:
                st.warning("No stock available to assign.")
                return
            df.loc[df['id'] == selected_id, 'quantity'] = current_qty - 1
            new_assignment = {
                "user": user,
                "role": role,
                "stock_id": selected_id,
                "stock_name": stock['name'].values[0],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "remarks": remarks,
                "status": "Assigned",
                "teacher_id": teacher_id if role == "Teacher" else "",
                "department": department if role == "Teacher" else "",
                "return_date": ""
            }
            assign_df = pd.concat([assign_df, pd.DataFrame([new_assignment])], ignore_index=True)
            save_data(df)
            save_assignments(assign_df)
            st.success("Product assigned successfully.")

def dashboard():
    st.title("📊 Dashboard Overview")
    df = load_data()
    st.subheader("📦 Stock Summary")
    low_stock_df = df[df['low_stock']]
    if not low_stock_df.empty:
        st.warning("⚠️ Low stock detected:")
        st.dataframe(low_stock_df[["name", "company", "category", "quantity", "price"]])
    else:
        st.success("All stock levels are sufficient.")
    st.dataframe(df[["id", "name", "company", "category", "quantity", "price", "low_stock"]])
    assign_df = load_assignments()
    st.subheader("👥 Assignment History")
    st.dataframe(assign_df)

# ---------- MAIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

def sidebar_nav():
    st.sidebar.image("https://img.icons8.com/color/96/box.png", width=80)
    st.sidebar.markdown("### <span style='color:#1565c0;'>Smart Inventory</span>", unsafe_allow_html=True)
    pages = [
        ("Home", "🏠 Home"),
        ("Add Stock", "➕ Add Stock"),
        ("Manage Stock", "🛠 Manage Stock"),
        ("View Stock", "🔍 View Stock"),
        ("Assign/Return", "👥 Assign/Return"),
        ("Dashboard", "📊 Dashboard"),
        ("Logout", "🚪 Logout")
    ]
    for key, label in pages:
        if st.sidebar.button(label, use_container_width=True, key=key):
            st.session_state.page = key
            if key == "Logout":
                st.session_state.logged_in = False
            st.rerun()

if not st.session_state.logged_in:
    login()
else:
    sidebar_nav()
    page = st.session_state.page
    if page == "Home":
        st.title("📦 Smart Inventory Management System")
        st.markdown("Manage your stock and assignments efficiently.")
    elif page == "Add Stock":
        add_stock()
    elif page == "Manage Stock":
        manage_stock()
    elif page == "View Stock":
        view_stock()
    elif page == "Assign/Return":
        assign_product()
    elif page == "Dashboard":
        dashboard()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.rerun()
