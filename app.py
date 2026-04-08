import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Ravi Tea", layout="centered")

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

# ---------------- GOOGLE SHEETS ----------------
@st.cache_resource
def connect_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    return client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1TUKZyDy-Ot2VtSuYln5XKz6ICPaZ5XOuYWKUdDSRHiI"
    ).sheet1

sheet = connect_sheet()

# ---------------- SESSION ----------------
st.session_state.setdefault("paid", False)
st.session_state.setdefault("last_click_time", None)

# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()

# ---------------- DB FUNCTIONS ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    return next((i + 1 for i, val in enumerate(phones) if val == phone), None)

def get_points(phone):
    row = find_row(phone)
    return int(sheet.cell(row, 2).value) if row else 0

def update_points(phone):
    row = find_row(phone)

    if row:
        current = int(sheet.cell(row, 2).value)
        new_points = current + 1
        sheet.update_cell(row, 2, new_points)
        return new_points
    else:
        sheet.append_row([phone, 1])
        return 1

# ---------------- FRAUD PREVENTION ----------------
def can_click():
    now = datetime.now()

    last = st.session_state.last_click_time
    if last is None or (now - last).seconds >= 10:
        st.session_state.last_click_time = now
        return True

    return False

# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.caption(TAGLINE)
st.divider()

# ---------------- PAYMENT ----------------
st.link_button("💸 Pay & Earn Rewards", UPI_LINK)
st.caption("After payment, confirm below 👇")

if st.button("✅ I Paid"):

    if not can_click():
        st.error("⛔ Wait few seconds before clicking again")
    else:
        st.session_state.paid = True
        st.balloons()

        st.markdown(f"""
        ### 🎉 Payment Successful!
        **at {SHOP_NAME}**
        ✅ You earned 1 point
        """)

# ---------------- SAVE + POINTS ----------------
if st.session_state.paid:

    phone = st.text_input(
        "💾 Save points & get FREE tea 🎁",
        placeholder="+91XXXXXXXXXX"
    )

    if st.button("💾 Save Rewards"):

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number like +919876543210")

        else:
            new_points = update_points(phone)

            st.success(f"🔥 {new_points}/5 points collected")
            st.progress(min(new_points / 5, 1.0))

            st.markdown(
                f"🎁 Only {max(0, 5 - new_points)} more for FREE TEA ☕"
            )

            if new_points >= 5:
                st.success("🎉 FREE TEA unlocked!")

    # ALWAYS SHOW CURRENT STATUS
    if phone and is_valid_phone(phone):
        current = get_points(phone)

        st.markdown("---")
        st.write(f"🔥 Total: {current}/5 points")
        st.progress(min(current / 5, 1.0))

# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")