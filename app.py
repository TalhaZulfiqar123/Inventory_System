import streamlit as st
import pandas as pd
import os
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

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
    .main-title {
        font-size: 2.8rem;
        color: #1565c0;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.5rem;
        color: #42a5f5;
        font-weight: 600;
        margin-bottom: 0.5em;
    }
    .desc {
        font-size: 1.1rem;
        color: #1976d2;
        margin-bottom: 2em;
    }
    .assign-detail {
        background: #e3f2fd;
        border-radius: 10px;
        padding: 1.2em 1em;
        margin-bottom: 1em;
        font-size: 1.08em;
        color: #1a237e;
        box-shadow: 0 2px 8px #90caf955;
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
IMAGE_FOLDER = "product_images"
USERS = {"admin": "admin123", "staff": "staff123"}

os.makedirs(BARCODE_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ---------- DATA FUNCTIONS ----------
def load_data():
    if os.path.exists(STOCK_FILE):
        df = pd.read_csv(STOCK_FILE, dtype=str)
        for col in ["company", "category", "image"]:
            if col not in df.columns:
                df[col] = ""
        df['quantity'] = df['quantity'].astype(int)
        df['price'] = df['price'].astype(float)
        df['low_stock'] = df['quantity'] < 5
        return df
    return pd.DataFrame(columns=["id", "name", "company", "category", "quantity", "price", "barcode", "image", "low_stock"])

def save_data(df):
    df.to_csv(STOCK_FILE, index=False)

def load_assignments():
    cols = ["user", "role", "stock_id", "stock_name", "date", "remarks", "status", "teacher_id", "department", "return_date"]
    if os.path.exists(ASSIGNMENT_FILE):
        df = pd.read_csv(ASSIGNMENT_FILE, dtype=str)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_assignments(df):
    df.to_csv(ASSIGNMENT_FILE, index=False)

def generate_barcode(uid):
    barcode_path = os.path.join(BARCODE_FOLDER, f"{uid}.png")
    Code128(str(uid), writer=ImageWriter()).write(open(barcode_path, 'wb'))
    return barcode_path

def save_image(uploaded_file, product_code):
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_path = os.path.join(IMAGE_FOLDER, f"{product_code}_{uploaded_file.name}")
        img.save(img_path)
        return img_path
    return ""

# ---------- LOGIN ----------
def login():
    # st.sidebar.image("https://img.icons8.com/color/96/box.png", width=80)
    # st.sidebar.markdown("### <span style='color:#1565c0;'>Smart Inventory</span>", unsafe_allow_html=True)
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
        uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])
        st.markdown("<br>", unsafe_allow_html=True)
        add_btn = st.button("Add Stock", use_container_width=True)

    if add_btn:
        if not product_code or not name or company in ["Select...", ""] or category in ["Select...", ""]:
            st.warning("Please fill out all required fields.")
            return
        df = load_data()

        # Check for existing product by name, company, category
        match = (df['name'] == name) & (df['company'] == company) & (df['category'] == category)
        image_path = save_image(uploaded_file, product_code)
        if match.any():
            idx = df[match].index[0]
            df.at[idx, 'quantity'] = int(df.at[idx, 'quantity']) + int(quantity)
            df.at[idx, 'price'] = price  # Optionally update price
            if image_path:
                df.at[idx, 'image'] = image_path
            st.success(f"✅ Stock updated: {name} ({company}, {category}) - New Quantity: {df.at[idx, 'quantity']}")
            barcode_path = df.at[idx, 'barcode']
            image_to_show = df.at[idx, 'image']
        else:
            # New stock entry
            barcode_path = generate_barcode(product_code)
            new_row = {
                "id": product_code,
                "name": name,
                "company": company,
                "category": category,
                "quantity": quantity,
                "price": price,
                "barcode": barcode_path,
                "image": image_path,
                "low_stock": int(quantity) < 5
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"✅ Stock added: {name} ({company}, {category}) - ID: {product_code}")
            image_to_show = image_path
        save_data(df)
        img_col, bar_col = st.columns(2)
        if image_to_show and os.path.exists(image_to_show):
            with img_col:
                st.image(image_to_show, width=180, caption="Product Image")
        if os.path.exists(barcode_path):
            with bar_col:
                st.image(barcode_path, width=180, caption="Barcode")

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
        img_col, bar_col = st.columns(2)
        img_path = product.get('image', '')
        if isinstance(img_path, str) and img_path.strip() and os.path.exists(img_path):
            with img_col:
                st.image(img_path, width=200, caption="Product Image")
        barcode_path = product.get('barcode', '')
        if isinstance(barcode_path, str) and barcode_path.strip() and os.path.exists(barcode_path):
            with bar_col:
                st.image(barcode_path, width=200, caption="Barcode")

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
        product_id_str = str(product_id).lstrip("0").strip()
        df['id_stripped'] = df['id'].astype(str).str.lstrip("0").str.strip()
        stock = df[df['id_stripped'] == product_id_str]
        mask = (assign_df['stock_id'].astype(str).str.lstrip("0").str.strip() == product_id_str) & (assign_df['status'] == "Assigned")
        if not stock.empty and not assign_df[mask].empty:
            product = stock.iloc[0]
            latest_idx = assign_df[mask].index[-1]
            assignment = assign_df.loc[latest_idx]
            st.markdown(f"""
                <div class='assign-detail'>
                <b>Assignment Details:</b><br>
                <b>User:</b> {assignment['user']}<br>
                <b>Role:</b> {assignment['role']}<br>
                <b>Stock ID:</b> {assignment['stock_id']}<br>
                <b>Stock Name:</b> {assignment['stock_name']}<br>
                <b>Date:</b> {assignment['date']}<br>
                <b>Remarks:</b> {assignment['remarks']}<br>
                <b>Status:</b> {assignment['status']}
                </div>
            """, unsafe_allow_html=True)
            img_col, bar_col = st.columns(2)
            img_path = product.get('image', '')
            if isinstance(img_path, str) and img_path.strip() and os.path.exists(img_path):
                with img_col:
                    st.image(img_path, width=180, caption="Product Image")
            barcode_path = product.get('barcode', '')
            if isinstance(barcode_path, str) and barcode_path.strip() and os.path.exists(barcode_path):
                with bar_col:
                    st.image(barcode_path, width=180, caption="Barcode")
            if st.button("Return Product"):
                assign_df.at[latest_idx, 'status'] = "Returned"
                assign_df.at[latest_idx, 'return_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                df.loc[df['id_stripped'] == product_id_str, 'quantity'] = int(df[df['id_stripped'] == product_id_str]['quantity'].values[0]) + 1
                save_data(df.drop(columns=['id_stripped']))
                save_assignments(assign_df)
                st.success("Product returned successfully.")
        elif not stock.empty:
            st.warning("No outstanding assignment found for this stock ID.")
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
            if int(current_qty) <= 0:
                st.warning("No stock available to assign.")
                return
            df.loc[df['id'] == selected_id, 'quantity'] = int(current_qty) - 1
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


#Load the logo image
logo = Image.open("assets/logo.png")



def sidebar_nav():
    st.sidebar.image( logo ,width=140)
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

# def home_page():
#     st.markdown("""
#         <div style='text-align:center; margin-top:2em;'>
#             <img src="{logo_path}" width="90"/>
#             <div class='main-title'>Smart Inventory Management System</div>
#             <div class='subtitle'>Efficient, Reliable, and Visual Stock Control</div>
#             <div class='desc'>
#                 Welcome to your digital inventory assistant! <br>
#                 Seamlessly manage product stock, assignments, and returns for your organization.<br>
#                 <b>Features:</b> Barcode tracking, image uploads, low-stock alerts, and more.
#             </div>
#         </div>
#     """, unsafe_allow_html=True)
def home_page():
    st.markdown("""
        <div style="text-align: center; margin-top: 2em;">
            <h1 style="font-size: 2.8rem; color: #2c3e50;">🏫 Smart University Inventory Management</h1>
            <p style="font-size: 1.1rem; color: #34495e;">Digitally manage university assets — track, assign, return, and monitor your stock with ease.</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

    # Columns layout: content + static logo
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
            <h3 style="color: #1a237e;">📋 Key Features</h3>
            <ul>
                <li>Barcode-based Inventory Tracking</li>
                <li>Assign & Return Assets</li>
                <li>Teacher/Student Management</li>
                <li>Excel Integration</li>
                <li>Real-time Dashboard</li>
            </ul>
        """, unsafe_allow_html=True)

    with col2:
        st.image("assets/logo.png", caption="Website Logo", use_container_width=True)


    st.markdown("<hr>", unsafe_allow_html=True)

    # Footer with username and date
    st.markdown("""
        <div style="text-align: center;">
            <h4 style="color:#1565c0;">Logged in as: <span style="color:#2e7d32;">{}</span></h4>
            <p style="color:#546e7a;">Today's Date: {}</p>
        </div>
    """.format(
        st.session_state.get("username", "Unknown"),
        datetime.today().strftime('%B %d, %Y')
    ), unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
else:
    sidebar_nav()
    page = st.session_state.page
    if page == "Home":
        home_page()
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
