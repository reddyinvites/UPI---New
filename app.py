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


# ---------------- FIND ROW ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if val == phone:
            return i + 1
    return None


# ---------------- GET POINTS ----------------
def get_points(phone):
    row = find_row(phone)
    if row:
        return int(sheet.cell(row, 2).value)
    return 0


# ---------------- UPDATE POINTS ----------------
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
st.write(TAGLINE)

st.divider()

# ---------------- PAYMENT ----------------
st.markdown("### 💸 Pay & Earn Rewards")
st.link_button("👉 Pay with UPI", UPI_LINK)

st.write("👇 After payment, confirm below")

if st.button("✅ I Paid"):

    if not can_click():
        st.error("⛔ Wait few seconds before clicking again")
    else:
        st.session_state.paid = True
        st.balloons()

        st.markdown(f"""
        ## 🎉 Payment Successful!

        **at {SHOP_NAME}**

        ✅ You earned 1 point  
        🔥 Complete 5 → get FREE TEA ☕
        """)


# ---------------- SAVE + REWARDS ----------------
if st.session_state.paid:

    phone = st.text_input(
        "💾 Save your rewards (WhatsApp number)",
        placeholder="+91XXXXXXXXXX"
    )

    if st.button("💾 Save Rewards"):

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number like +919876543210")

        else:
            points = update_points(phone)

            st.success(f"🔥 {points}/5 points collected")
            st.progress(min(points / 5, 1.0))

            # 🔥 NEW SMART MESSAGE
            remaining = max(0, 5 - points)

            if remaining > 0:
                st.markdown(
                    f"🔥 Just {remaining} more tea{'s' if remaining > 1 else ''} to get FREE TEA ☕"
                )
            else:
                st.markdown("🎉 FREE TEA unlocked! ☕")

            if points >= 5:
                st.success("🎉 FREE TEA unlocked!")

            st.rerun()


# ---------------- SHOW REWARDS ALWAYS ----------------
if st.session_state.paid and phone and is_valid_phone(phone):

    current = get_points(phone)

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(current / 5, 1.0))
    st.write(f"🔥 {current}/5 points collected")

    if current >= 5:
        st.success("🎉 FREE TEA unlocked!")


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")