import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Ravi Tea", layout="centered")

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


# ---------------- SESSION ----------------
if "paid" not in st.session_state:
    st.session_state.paid = False

if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = None


# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- GET POINTS ----------------
def get_points(phone):
    data = sheet.get_all_records()
    total = 0

    for row in data:
        if row["Phone"] == phone:
            total += row["Points"]

    return total


# ---------------- UPDATE POINTS (NO DUPLICATES) ----------------
def update_points(phone):
    data = sheet.get_all_records()

    total = 0
    main_row = None
    delete_rows = []

    for i, row in enumerate(data):
        if row["Phone"] == phone:
            total += row["Points"]

            if main_row is None:
                main_row = i + 2
            else:
                delete_rows.append(i + 2)

    # delete duplicate rows
    for r in reversed(delete_rows):
        sheet.delete_rows(r)

    if main_row:
        new_points = total + 1
        sheet.update_cell(main_row, 2, new_points)
        return new_points

    # new user
    sheet.append_row([phone, 1])
    return 1


# ---------------- FRAUD PREVENTION ----------------
def can_click():
    now = datetime.now()

    if st.session_state.last_click_time is None:
        st.session_state.last_click_time = now
        return True

    diff = (now - st.session_state.last_click_time).seconds

    if diff < 10:
        return False
    else:
        st.session_state.last_click_time = now
        return True


# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.caption(TAGLINE)

st.divider()

# PAY
st.link_button("💸 Pay & Earn Rewards", UPI_LINK)
st.caption("After payment, confirm below 👇")

paid_click = st.button("✅ I Paid")


# ---------------- SUCCESS ----------------
if paid_click:

    if not can_click():
        st.error("⛔ Wait few seconds before clicking again")
    else:
        st.session_state.paid = True
        st.balloons()
        st.success("🎉 Payment Successful!")


# ---------------- SAVE + LOYALTY ----------------
if st.session_state.paid:

    phone = st.text_input(
        "💾 Save points & get FREE tea 🎁",
        placeholder="+91XXXXXXXXXX"
    )

    if st.button("💾 Save Rewards"):

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number like +919876543210")

        else:
            # update + get latest
            update_points(phone)
            current = get_points(phone)

            st.success(f"🔥 {current}/5 points collected")
            st.progress(min(current / 5, 1.0))

            st.markdown(f"""
            🎁 Only {max(0, 5 - current)} more for FREE TEA ☕
            """)

            if current >= 5:
                st.success("🎉 FREE TEA unlocked!")

    # ALWAYS SHOW CURRENT STATUS
    if phone and is_valid_phone(phone):
        current = get_points(phone)

        st.divider()
        st.write(f"🔥 Total: {current}/5 points")
        st.progress(min(current / 5, 1.0))


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")