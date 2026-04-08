import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Rewards Platform", layout="centered")

# ---------------- GOOGLE SHEETS ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1TUKZyDy-Ot2VtSuYln5XKz6ICPaZ5XOuYWKUdDSRHiI"
).sheet1


# ---------------- SHOPS ----------------
SHOPS = {
    "ravi-tea": {"name": "RAVI TEA ☕", "tagline": "Morning kick chai 🔥"},
    "juice-corner": {"name": "JUICE CORNER 🧃", "tagline": "Fresh juice 🍊"}
}


# ---------------- GET QUERY ----------------
query = st.query_params

role = query.get("role", "customer")
shop_id = query.get("shop", "ravi-tea")

if isinstance(role, list): role = role[0]
if isinstance(shop_id, list): shop_id = shop_id[0]

shop = SHOPS.get(shop_id, SHOPS["ravi-tea"])


# ---------------- COMMON FUNCTIONS ----------------
def get_all_data():
    return pd.DataFrame(sheet.get_all_records())

def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if val == phone:
            return i + 1
    return None

def update_points(phone):
    row = find_row(phone)
    if row:
        current = int(sheet.cell(row, 2).value)
        new = current + 1
        sheet.update_cell(row, 2, new)
        return new
    else:
        sheet.append_row([phone, 1])
        return 1


# =========================================================
# 👤 CUSTOMER PAGE
# =========================================================
if role == "customer":

    st.title(shop["name"])
    st.caption(shop["tagline"])

    st.divider()

    st.link_button("💸 Pay & Earn Rewards", "upi://pay")

    if st.button("✅ I Paid"):
        st.success("🎉 Payment Successful!")

    phone = st.text_input("Enter phone")

    if st.button("Save"):
        points = update_points(phone)
        st.success(f"{points}/5 points")


# =========================================================
# 🏪 OWNER DASHBOARD
# =========================================================
elif role == "owner":

    st.title(f"🏪 {shop['name']} Dashboard")

    data = get_all_data()

    st.subheader("📊 Customers")
    st.dataframe(data)

    total_customers = len(data)
    total_points = data["Points"].sum() if not data.empty else 0

    st.metric("👥 Total Customers", total_customers)
    st.metric("🔥 Total Points Given", total_points)


# =========================================================
# 🧠 ADMIN DASHBOARD
# =========================================================
elif role == "admin":

    st.title("🧠 Admin Dashboard")

    st.subheader("🏪 All Shops")

    for key, val in SHOPS.items():
        st.write(f"👉 {val['name']}")
        st.code(f"?role=owner&shop={key}")

    st.divider()

    data = get_all_data()

    st.subheader("📊 Full Data")
    st.dataframe(data)