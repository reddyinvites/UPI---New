import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ---------------- GOOGLE SHEETS SETUP ----------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("TeaCustomers").sheet1  # your sheet name

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

# ---------------- SESSION ----------------
if "paid" not in st.session_state:
    st.session_state.paid = False

# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()

# ---------------- GOOGLE SHEETS FUNCTIONS ----------------
def get_points(phone):
    data = sheet.get_all_records()
    for row in data:
        if row["Phone"] == phone:
            return row["Points"]
    return 0

def update_points(phone):
    data = sheet.get_all_records()

    for i, row in enumerate(data):
        if row["Phone"] == phone:
            new_points = row["Points"] + 1
            sheet.update_cell(i + 2, 2, new_points)
            return new_points

    # New user
    sheet.append_row([phone, 1])
    return 1

# ---------------- UI ----------------
st.title(SHOP_NAME)
st.write(TAGLINE)

st.divider()

phone = st.text_input("💾 Save rewards (Enter WhatsApp number)", placeholder="+91XXXXXXXXXX")

st.link_button("💸 Pay with UPI", UPI_LINK)

if st.button("✅ I Paid"):
    if not is_valid_phone(phone):
        st.error("❌ Enter valid number like +919876543210")
    else:
        st.session_state.paid = True
        points = update_points(phone)

        st.balloons()

        st.success("🎉 Payment Successful!")
        st.write(f"at {SHOP_NAME}")
        st.write(f"✅ You earned 1 point")
        st.write(f"🔥 Only {5 - points} more for FREE TEA")

# ---------------- SHOW CURRENT POINTS ----------------
if phone and is_valid_phone(phone):
    current = get_points(phone)

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(current / 5, 1.0))
    st.write(f"🔥 {current}/5 points collected")

    if current >= 5:
        st.success("🎉 FREE TEA unlocked!")