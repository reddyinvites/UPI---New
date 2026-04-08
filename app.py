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

        # ⏱ COOLDOWN
        if last_time:
            last_time = datetime.fromisoformat(last_time)
            diff = (now - last_time).total_seconds() / 60

            if diff < COOLDOWN_MINUTES:
                return current_points, False, int(COOLDOWN_MINUTES - diff)

        new_points = current_points + 1

        sheet.update_cell(row_index, 2, new_points)
        sheet.update_cell(row_index, 3, now.isoformat())

        return new_points, True, None

    else:
        sheet.append_row([phone, 1, now.isoformat()])
        return 1, True, None

def redeem_reward(phone):
    row_index, row = get_user_row(phone)
    if row:
        sheet.update_cell(row_index, 2, 0)

# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)

st.divider()

# ---------------- PHONE INPUT ----------------
phone = st.text_input(
    "📱 Enter your number",
    placeholder="+91XXXXXXXXXX"
)

# ---------------- MAIN LOGIC ----------------
if phone and is_valid_phone(phone):

    row_index, row = get_user_row(phone)
    points = row["Points"] if row else 0
    points = min(points, 5)

    # 🎉 FREE TEA STATE
    if points >= 5:
        st.success("🎉 FREE TEA unlocked!")
        st.markdown("👉 Show this to shop owner ☕")

        if st.button("☕ Redeem Free Tea"):
            redeem_reward(phone)
            st.success("✅ Redeemed! Start again 🔥")
            st.session_state.points = 0

    # 💸 NORMAL STATE
    else:
        st.subheader("💸 Pay & Earn Rewards")

        st.link_button("👉 Pay with UPI", UPI_LINK)
        st.write("👇 After payment, confirm below")

        if st.button("✅ I Paid"):
            st.session_state.paid = True

        if st.session_state.paid:
            if st.button("💾 Save Rewards"):

                new_points, success, wait = update_points(phone)
                st.session_state.points = new_points

                if not success and wait:
                    st.warning(f"⏳ Come back in {wait} mins")

                elif success:
                    st.success("🎉 Payment Successful!")
                    st.write("✅ You earned 1 point")

    # ---------------- REWARDS ----------------
    st.divider()
    st.subheader("🎁 Your Rewards")

    display_points = st.session_state.points if st.session_state.points else points
    display_points = min(display_points, 5)

    st.progress(display_points / 5)
    st.write(f"🔥 {display_points}/5 points collected")

    if display_points < 5:
        remaining = 5 - display_points
        st.write(f"🔥 Just {remaining} more tea to get FREE TEA ☕")

    if display_points >= 5:
        st.success("🎉 FREE TEA unlocked!")

elif phone:
    st.error("❌ Enter valid number like +919876543210")