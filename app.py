import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

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
for key in ["phone", "points", "paid_clicked", "success_msg", "submitted", "end_screen"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "points" else 0

# fix phone separately
if not isinstance(st.session_state.phone, str):
    st.session_state.phone = ""


# ---------------- HELPERS ----------------
def clean_phone(p):
    return str(p).strip().replace(" ", "")


def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if clean_phone(val) == phone:
            return i + 1
    return None


def get_user_data(phone):
    row = find_row(phone)
    if row:
        return int(sheet.cell(row, 2).value)
    return 0


def update_points(phone):
    row = find_row(phone)
    now = datetime.now()

    if row:
        pts = int(sheet.cell(row, 2).value) + 1
        sheet.update_cell(row, 2, pts)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))
        return pts
    else:
        sheet.append_row([phone, 1, now.strftime("%Y-%m-%d %H:%M:%S")])
        return 1


# ---------------- HEADER ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)
st.divider()


# =========================================================
# END SCREEN
# =========================================================
if st.session_state.end_screen:

    st.markdown("""
### 🎯 See you again!

🔥 Every tea = reward  
🎁 Every 5 = FREE tea  

👉 Come back soon  
👉 More visits = more free chai ☕
""")

    st.caption("Powered by Your Startup 🚀")
    st.stop()


# =========================================================
# WELCOME SCREEN
# =========================================================
if not st.session_state.submitted:

    st.markdown("""
### ☕ Welcome to RAVI TEA

🔥 Morning kick chai that boosts your day  

💸 Pay easily with UPI  
🎁 Earn rewards on every tea  
☕ Complete 5 → Get 1 FREE  
""")

    st.info("🚀 Smart Rewards System")

    with st.form("form"):
        phone = st.text_input("📱 Enter your number", placeholder="+91XXXXXXXXXX")
        submit = st.form_submit_button("Check")

    if submit:
        phone = clean_phone(phone)

        if is_valid_phone(phone):
            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("❌ Enter valid number")


# =========================================================
# MAIN FLOW
# =========================================================
if st.session_state.submitted:

    pts = st.session_state.points

    # welcome message
    if pts == 0:
        st.success("👋 Welcome! Start earning rewards 🎉")
    else:
        st.success(f"👋 Welcome back! You have {pts} points")

    # ---------------- SUCCESS UI (ONLY CLEAN UI) ----------------
    if st.session_state.success_msg:

        st.success("🎉 Payment Successful! +1 point added")

        st.markdown(f"""
**at {SHOP_NAME}**

✅ You earned 1 point  
🔥 Complete 5 → get FREE TEA ☕
""")

    # ---------------- NORMAL FLOW ----------------
    elif pts < 5:

        st.markdown("### 💸 Get your reward")
        st.link_button("👉 Pay with UPI", UPI_LINK)

        if st.button("✅ I Paid"):
            st.session_state.paid_clicked = True
            st.session_state.points = update_points(st.session_state.phone)
            st.session_state.success_msg = True
            st.rerun()

    # ---------------- FREE TEA ----------------
    if pts >= 5:
        st.success("🎉 FREE TEA unlocked!")
        st.markdown("👉 Show this screen to shop owner ☕")

    # ---------------- REWARDS (ONLY ONCE CLEAN) ----------------
    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(st.session_state.points / 5, 1.0))
    st.write(f"🔥 {st.session_state.points}/5 points collected")

    remaining = max(0, 5 - st.session_state.points)

    if remaining > 0:
        st.write(f"🔥 {remaining} more teas to get FREE TEA ☕")


# =========================================================
# AUTO RESET → CLEAN END SCREEN
# =========================================================
if st.session_state.success_msg:

    time.sleep(10)

    st.session_state.phone = ""
    st.session_state.points = 0
    st.session_state.paid_clicked = False
    st.session_state.success_msg = False
    st.session_state.submitted = False
    st.session_state.end_screen = True

    st.rerun()


# ---------------- FOOTER ----------------
st.caption("Powered by Your Startup 🚀")