import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="RAVI TEA ☕", layout="centered")

st.title("RAVI TEA ☕")
st.write("Morning kick chai 🔥")

# ---------------- GOOGLE SHEETS ----------------
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

SHEET_ID = "YOUR_SHEET_ID"
sheet = client.open_by_key(SHEET_ID).sheet1

# ---------------- NORMALIZE FUNCTION (FIX) ----------------
def normalize(phone):
    return str(phone).replace("+91", "").replace(" ", "").strip()

# ---------------- GET USER ----------------
def get_user_row(phone):
    data = sheet.get_all_records()

    for i, row in enumerate(data):
        sheet_phone = normalize(row["Phone"])
        input_phone = normalize(phone)

        if sheet_phone == input_phone:
            return i + 2, row

    return None, None

# ---------------- UI ----------------
phone = st.text_input("📱 Enter your number", placeholder="+91XXXXXXXXXX")

st.markdown("---")

st.subheader("💸 Pay & Earn Rewards")

st.button("👉 Pay with UPI")

st.write("👇 After payment, confirm below")

paid = st.button("✅ I Paid")

# ---------------- MAIN LOGIC ----------------
if phone:
    row_index, user = get_user_row(phone)

    # Existing user
    if user:
        points = int(user["Points"])
        last_time = user.get("LastTime", "")

    else:
        points = 0
        last_time = ""

    # ---------------- PAYMENT ----------------
    if paid:
        if row_index:
            # Update existing
            new_points = points + 1
            sheet.update_cell(row_index, 2, new_points)
            sheet.update_cell(row_index, 3, str(datetime.now()))
        else:
            # New user
            sheet.append_row([phone, 1, str(datetime.now())])
            new_points = 1

        st.success("🎉 Payment Successful!")
        st.write("✅ You earned 1 point")

        # Refresh values
        points = new_points

    # ---------------- REWARDS DISPLAY ----------------
    st.markdown("---")
    st.subheader("🎁 Your Rewards")

    display_points = min(points, 5)

    progress = display_points / 5
    st.progress(progress)

    st.write(f"🔥 {display_points}/5 points collected")

    remaining = 5 - display_points

    if points >= 5:
        st.success("🎉 FREE TEA unlocked!")
        st.write("👉 Show this screen to shop owner ☕")

    else:
        st.write(f"🔥 Just {remaining} more tea to get FREE TEA ☕")

    st.markdown("---")

# ---------------- FOOTER ----------------
st.write("Powered by Your Startup 🚀")