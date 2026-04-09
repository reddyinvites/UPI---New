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
if "phone" not in st.session_state:
    st.session_state.phone = ""

if "points" not in st.session_state:
    st.session_state.points = 0

if "paid_clicked" not in st.session_state:
    st.session_state.paid_clicked = False

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
# 🟢 END SCREEN
# =========================================================
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


# =========================================================
# 🟢 WELCOME SCREEN
# =========================================================
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
            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("❌ Enter valid number (+91XXXXXXXXXX)")


# =========================================================
# 🟢 MAIN FLOW (NO DUPLICATES)
# =========================================================
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

        updated_pts = st.session_state.points

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(updated_pts / 5, 1.0))
        st.write(f"🔥 {updated_pts}/5 points collected")

        remaining = max(0, 5 - updated_pts)

        if remaining > 0:
            st.write(f"🔥 {remaining} more teas to get FREE TEA ☕")
        else:
            st.success("🎉 FREE TEA unlocked!")

    else:
        # -------- NORMAL FLOW --------
        if pts == 0:
            st.success("👋 Welcome! Start earning rewards 🎉")
        else:
            st.success(f"👋 Welcome back! You have {pts} points")

        if pts < 5:

            st.markdown("### 💸 Get your reward")

            st.link_button("👉 Pay with UPI", UPI_LINK)

            st.caption("💡 Complete payment using any UPI app")
            st.caption("👇 After payment, click below")

            if st.button("✅ I Paid"):
                new_pts = update_points(phone)

                st.session_state.points = new_pts
                st.session_state.success_msg = True

                st.rerun()

        # -------- REWARDS --------
        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(pts / 5, 1.0))
        st.write(f"🔥 {pts}/5 points collected")

        remaining = max(0, 5 - pts)

        if remaining > 0:
            st.write(f"🔥 {remaining} more teas to get FREE TEA ☕")
        else:
            st.success("🎉 FREE TEA unlocked!")


# =========================================================
# 🔁 AUTO RESET AFTER 10 SEC
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
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")