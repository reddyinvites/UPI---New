import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Tea Loyalty", layout="centered")

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

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

# ---------------- SETTINGS ----------------
COOLDOWN_MINUTES = 120

# ---------------- SESSION ----------------
if "paid" not in st.session_state:
    st.session_state.paid = False

if "points" not in st.session_state:
    st.session_state.points = 0

# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()

# ---------------- DB FUNCTIONS ----------------
def get_user_row(phone):
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row["Phone"] == phone:
            return i + 2, row
    return None, None

def update_points(phone):
    row_index, row = get_user_row(phone)

    now = datetime.now()

    if row:
        current_points = row["Points"]
        last_time = row.get("LastTime")

        # 🔒 STOP AFTER 5
        if current_points >= 5:
            return 5, False, None

        # ⏱ COOLDOWN CHECK
        if last_time:
            last_time = datetime.fromisoformat(last_time)
            diff = (now - last_time).total_seconds() / 60

            if diff < COOLDOWN_MINUTES:
                return current_points, False, int(COOLDOWN_MINUTES - diff)

        # ✅ ADD POINT
        new_points = current_points + 1

        sheet.update_cell(row_index, 2, new_points)
        sheet.update_cell(row_index, 3, now.isoformat())

        return new_points, True, None

    else:
        # NEW USER
        sheet.append_row([phone, 1, now.isoformat()])
        return 1, True, None

# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)

st.divider()

# PAY
st.subheader("💸 Pay & Earn Rewards")
st.link_button("👉 Pay with UPI", UPI_LINK)
st.write("👇 After payment, confirm below")

if st.button("✅ I Paid"):
    st.session_state.paid = True

# PHONE INPUT
phone = st.text_input(
    "💾 Save points & get FREE tea 🎁",
    placeholder="+91XXXXXXXXXX"
)

# SAVE BUTTON
if st.session_state.paid:

    if phone and is_valid_phone(phone):

        row_index, row = get_user_row(phone)
        current_points = row["Points"] if row else 0

        # 🔒 DISABLE IF ALREADY 5
        if current_points >= 5:
            st.success("🎉 FREE TEA unlocked!")
            st.markdown("👉 Show this screen to shop owner ☕")

            st.session_state.points = 5

        else:
            if st.button("💾 Save Rewards"):

                points, success, wait = update_points(phone)
                st.session_state.points = points

                if not success and wait:
                    st.warning(f"⏳ Come back in {wait} mins for next reward ☕")

                elif success:
                    st.success("🎉 Payment Successful!")
                    st.write(f"✅ You earned 1 point")

    elif phone:
        st.error("❌ Enter valid number like +919876543210")

# ---------------- REWARDS UI ----------------
if phone and is_valid_phone(phone):

    points = min(st.session_state.points, 5)

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(points / 5)
    st.write(f"🔥 {points}/5 points collected")

    # REMAINING MESSAGE
    if points < 5:
        remaining = 5 - points
        st.write(f"🔥 Just {remaining} more tea to get FREE TEA ☕")

    # FREE STATE
    if points >= 5:
        st.success("🎉 FREE TEA unlocked!")