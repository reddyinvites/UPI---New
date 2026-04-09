import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
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
if "phone" not in st.session_state:
    st.session_state.phone = ""

if "points" not in st.session_state:
    st.session_state.points = 0

if "success_msg" not in st.session_state:
    st.session_state.success_msg = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "end_screen" not in st.session_state:
    st.session_state.end_screen = False


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

    COOLDOWN_HOURS = 3

    if row:
        current_points = int(sheet.cell(row, 2).value)
        last_time_str = sheet.cell(row, 3).value

        if last_time_str:
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            diff = now - last_time

            if diff < timedelta(hours=COOLDOWN_HOURS):
                remaining = timedelta(hours=COOLDOWN_HOURS) - diff
                return current_points, False, remaining

        new_points = current_points + 1

        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))

        return new_points, True, None

    else:
        sheet.append_row([
            phone,
            1,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ])
        return 1, True, None


# ---------------- HEADER ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)
st.divider()


# ---------------- END SCREEN ----------------
if st.session_state.end_screen:
    st.markdown(f"""
### 🎯 See you again!

🔥 *{TAGLINE}*

💸 Every tea = reward  
🎁 Every 5 = FREE tea  
""")
    st.stop()


# ---------------- WELCOME ----------------
if not st.session_state.submitted:

    st.markdown("""
### ☕ Welcome to RAVI TEA
👇 Enter number to start
""")

    with st.form("form"):
        phone = st.text_input("📱 Enter your number")
        submit = st.form_submit_button("Check")

    if submit:
        phone = clean_phone(phone)

        if is_valid_phone(phone):
            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("❌ Invalid number")

    st.stop()


# =================================================
# 🔥 MAIN UI IN SINGLE CONTAINER (ULTIMATE FIX)
# =================================================
main = st.container()

with main:

    phone = st.session_state.phone
    pts = st.session_state.points

    # -------- SUCCESS --------
    if st.session_state.success_msg:

        st.success("🎉 Payment Successful! +1 point added")

        st.markdown(f"""
**at {SHOP_NAME}**
✅ You earned 1 point  
🔥 Complete 5 → get FREE TEA ☕
""")

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(pts / 5, 1.0))
        st.write(f"{pts}/5 points")

        time.sleep(10)

        st.session_state.success_msg = False
        st.session_state.submitted = False
        st.session_state.end_screen = True

        st.rerun()
        return  # 🔥 HARD STOP


    # -------- NORMAL --------
    if pts == 0:
        st.success("👋 Welcome!")
    else:
        st.success(f"👋 You have {pts} points")

    if pts < 5:

        st.link_button("👉 Pay", UPI_LINK)

        if st.button("✅ I Paid"):
            new_pts, allowed, _ = update_points(phone)

            if allowed:
                st.session_state.points = new_pts
                st.session_state.success_msg = True
                st.rerun()
                return  # 🔥 HARD STOP

    # -------- REWARDS --------
    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(pts / 5, 1.0))
    st.write(f"{pts}/5 points")