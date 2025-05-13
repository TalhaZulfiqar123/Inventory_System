import streamlit as st
import pandas as pd
import uuid
import os
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter

# ---------- CONFIG ----------
STOCK_FILE = "stock.csv"
ASSIGNMENT_FILE = "assignments.csv"
BARCODE_FOLDER = "barcodes"
UPLOAD_FOLDER = "uploaded_codes"
USERS = {"admin": "admin123", "staff": "staff123"}

# ---------- SETUP ----------
os.makedirs(BARCODE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- LOGIN ----------
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

# ---------- DATA FUNCTIONS ----------
def load_data():
    if os.path.exists(STOCK_FILE):
        df = pd.read_csv(STOCK_FILE)
        df['low_stock'] = df['quantity'] < 5
        return df
    return pd.DataFrame(columns=["id", "name", "quantity", "price", "barcode", "low_stock"])

def save_data(df):
    df.to_csv(STOCK_FILE, index=False)

def load_assignments():
    cols = ["user", "role", "stock_id", "stock_name", "date", "remarks", "status", "teacher_id", "department"]
    if os.path.exists(ASSIGNMENT_FILE):
        return pd.read_csv(ASSIGNMENT_FILE)
    return pd.DataFrame(columns=cols)

def save_assignments(df):
    df.to_csv(ASSIGNMENT_FILE, index=False)

def generate_barcode(uid):
    barcode_path = os.path.join(BARCODE_FOLDER, f"{uid}.png")
    Code128(uid, writer=ImageWriter()).write(open(barcode_path, 'wb'))
    return barcode_path

# ---------- PAGE FUNCTIONS ----------
def upload_master_codes():
    st.title("📁 Upload Item Code Sheet")
    uploaded_file = st.file_uploader("Upload Excel file (Furniture, Machinery, IT)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("✅ Preview of Uploaded File:")
        st.dataframe(df.head())
        save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File saved to: {save_path}")
        if 'item Name' in df.columns:
            code_column = [col for col in df.columns if 'Unnamed' in col or 'code' in col.lower()]
            if code_column:
                df = df.rename(columns={code_column[0]: 'code'})
                code_map = dict(zip(df['item Name'], df['code']))
                st.session_state.code_map = code_map
                st.success("Code map created and stored.")
            else:
                st.warning("⚠️ Code column not detected.")
        else:
            st.warning("⚠️ 'item Name' column not found.")

def add_stock():
    st.title("➕ Add New Stock")
    name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=1)
    price = st.number_input("Price", min_value=0.0, step=0.01)
    if 'code_map' in st.session_state and name in st.session_state.code_map:
        auto_code = st.session_state.code_map[name]
        st.success(f"Auto-detected Item Code: {auto_code}")
    if st.button("Add Stock"):
        uid = str(uuid.uuid4())[:8]
        barcode_path = generate_barcode(uid)
        df = load_data()
        new_row = {"id": uid, "name": name, "quantity": quantity, "price": price, "barcode": barcode_path}
        df = pd.concat([df, pd.DataFrame([new_row])])
        save_data(df)
        st.success(f"Stock added: {name} (ID: {uid})")
        if os.path.exists(barcode_path):
            st.image(barcode_path, width=200)

def manage_stock():
    st.title("🛠 Manage Stock")
    df = load_data()
    if df.empty:
        st.warning("No stock available.")
        return
    product_name = st.selectbox("Select Product Name to Manage", df['name'].tolist())
    stock = df[df['name'] == product_name]
    selected_id = st.selectbox("Select Stock ID", stock['id'].tolist())
    quantity = st.number_input("New Quantity", min_value=0, value=int(stock['quantity'].values[0]))
    price = st.number_input("New Price", min_value=0.0, step=0.01, value=float(stock['price'].values[0]))
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
    st.dataframe(df)
    product_name = st.selectbox("Select Product Name to View", df['name'].tolist())
    stock = df[df['name'] == product_name]
    if not stock.empty:
        selected_id = st.selectbox("Select Stock ID", stock['id'].tolist())
        product = stock[stock['id'] == selected_id].iloc[0]
        st.write(f"**Product Name**: {product['name']}")
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
        if st.button("Submit"):
            current_qty = stock['quantity'].values[0]
            new_qty = current_qty - 1 if action == "Assign" else current_qty + 1
            df.loc[df['id'] == selected_id, 'quantity'] = new_qty
            new_assignment = {
                "user": user,
                "role": role,
                "stock_id": selected_id,
                "stock_name": stock['name'].values[0],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "remarks": remarks,
                "status": "Assigned" if action == "Assign" else "Returned",
                "teacher_id": teacher_id if role == "Teacher" else "",
                "department": department if role == "Teacher" else ""
            }
            assign_df = pd.concat([assign_df, pd.DataFrame([new_assignment])])
            save_data(df)
            save_assignments(assign_df)
            st.success(f"Product {action.lower()}ed successfully.")

def dashboard():
    st.title("📊 Dashboard Overview")
    df = load_data()
    st.subheader("📦 Stock Summary")
    low_stock_df = df[df['low_stock']]
    if not low_stock_df.empty:
        st.warning("⚠️ Low stock detected:")
        st.dataframe(low_stock_df[['name', 'quantity', 'price']])
    else:
        st.success("All stock levels are sufficient.")
    st.dataframe(df)
    assign_df = load_assignments()
    st.subheader("👥 Assignment History")
    st.dataframe(assign_df)
    st.subheader("📁 Uploaded Code Sheets")
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        for file in files:
            try:
                df_uploaded = pd.read_excel(os.path.join(UPLOAD_FOLDER, file))
                with st.expander(f"🔽 {file}"):
                    st.dataframe(df_uploaded)
            except:
                st.warning(f"❌ Failed to read: {file}")
    else:
        st.info("No code files uploaded.")

# ---------- MAIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    menu = ["Home", "Add Stock", "Manage Stock", "View Stock", "Assign/Return", "Upload Item Codes", "Dashboard", "Logout"]
    choice = st.sidebar.radio("📋 Menu", menu)
    if choice == "Home":
        st.title("📦 Smart Inventory Management System")
        st.markdown("Manage your stock and assignments efficiently.")
    elif choice == "Add Stock":
        add_stock()
    elif choice == "Manage Stock":
        manage_stock()
    elif choice == "View Stock":
        view_stock()
    elif choice == "Assign/Return":
        assign_product()
    elif choice == "Upload Item Codes":
        upload_master_codes()
    elif choice == "Dashboard":
        dashboard()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()
