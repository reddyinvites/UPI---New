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

if "pay_timer_start" not in st.session_state:
    st.session_state.pay_timer_start = None


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

👉 Come back soon & scan again  
👉 More visits = more free chai ☕
""")

    st.caption("Powered by Your Startup 🚀")
    st.stop()


# ---------------- WELCOME ----------------
if not st.session_state.submitted:

    st.markdown("""
### ☕ Welcome to RAVI TEA

🔥 Morning kick chai that boosts your day  

💸 Pay easily with UPI  
🎁 Earn rewards on every tea  
☕ Complete 5 → Get 1 FREE  

👇 Just enter your number & start earning
""")

    st.info("🚀 Powered by Your Startup — Smart Rewards System")

    st.divider()

    with st.form("form"):
        phone = st.text_input("📱 Enter your number", placeholder="+91XXXXXXXXXX")
        submit = st.form_submit_button("Check")

    if submit:
        phone = clean_phone(phone)

        if is_valid_phone(phone):

            # RESET FIX
            st.session_state.success_msg = False
            st.session_state.end_screen = False
            st.session_state.pay_timer_start = None

            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True

            st.rerun()
        else:
            st.error("❌ Enter valid number (+91XXXXXXXXXX)")


# ---------------- MAIN FLOW ----------------
if st.session_state.submitted:

    phone = st.session_state.phone
    pts = st.session_state.points

    # -------- SUCCESS FLOW --------
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
        st.write(f"🔥 {pts}/5 points collected")

        if pts >= 5:
            st.success("🎉 FREE TEA unlocked!")

        time.sleep(10)

        st.session_state.phone = ""
        st.session_state.points = 0
        st.session_state.success_msg = False
        st.session_state.submitted = False
        st.session_state.end_screen = True
        st.session_state.pay_timer_start = None

        st.rerun()
        st.stop()

    # -------- NORMAL FLOW --------
    if pts == 0:
        st.success("👋 Welcome! Start earning rewards 🎉")
    else:
        st.success(f"👋 Welcome back! You have {pts} points")

    if pts < 5:

        st.markdown("### 💸 Get your reward")

        st.link_button("👉 Pay with UPI", UPI_LINK)

        st.caption("💡 Complete payment using any UPI app")

        # ✅ FIXED TIMER (NO FREEZE)
        if st.session_state.pay_timer_start is None:
            st.session_state.pay_timer_start = datetime.now()

        elapsed = (datetime.now() - st.session_state.pay_timer_start).total_seconds()

        if elapsed < 3:
            st.warning("👉 Open UPI app & come back to confirm")
            enable_paid = False
        else:
            enable_paid = True

        st.caption("👇 After payment, click below")

        if st.button("✅ I Paid", disabled=not enable_paid):

            new_pts, allowed, remaining_time = update_points(phone)

            if not allowed:
                mins = int(remaining_time.total_seconds() // 60)
                st.warning(f"⏳ Come back in {mins} mins for next reward ☕")
            else:
                st.session_state.points = new_pts
                st.session_state.success_msg = True
                st.session_state.pay_timer_start = None
                st.rerun()

    # -------- REWARDS --------
    if not st.session_state.success_msg:

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(pts / 5, 1.0))
        st.write(f"🔥 {pts}/5 points collected")

        remaining = max(0, 5 - pts)

        if remaining > 0:
            st.write(f"🔥 {remaining} more teas to get FREE TEA ☕")
        else:
            st.success("🎉 FREE TEA unlocked!")


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")