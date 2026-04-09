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


# ---------------- CLEAN PHONE ----------------
def clean_phone(p):
    return str(p).strip().replace(" ", "")


def is_valid_phone(phone):
    phone = clean_phone(phone)
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- FIND ROW ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if clean_phone(val) == phone:
            return i + 1
    return None


# ---------------- GET USER DATA ----------------
def get_user_data(phone):
    row = find_row(phone)
    if row:
        pts = int(sheet.cell(row, 2).value)
        last = sheet.cell(row, 3).value
        return pts, last
    return 0, None


# ---------------- UPDATE POINTS ----------------
def update_points(phone):
    row = find_row(phone)
    now = datetime.now()

    if row:
        current_points = int(sheet.cell(row, 2).value)
        new_points = current_points + 1

        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))

        return new_points
    else:
        sheet.append_row([
            phone,
            1,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ])
        return 1


# ---------------- UI HEADER ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)
st.divider()


# ---------------- END SCREEN ----------------
if st.session_state.end_screen:

    st.markdown(f"### 🎯 See you again at {SHOP_NAME}!")

    st.markdown("""
🔥 Every tea = reward  
🎁 Every 5 = FREE tea  

👉 Come back soon & scan again  
👉 More visits = more free chai ☕
""")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("🚀 Powered by Your Startup")

    st.stop()


# ---------------- INPUT ----------------
with st.form("phone_form"):
    phone = st.text_input(
        "📱 Enter your number to check rewards",
        value=st.session_state.phone,
        placeholder="+91XXXXXXXXXX",
        disabled=st.session_state.submitted
    )

    submit = st.form_submit_button("Check")


# ---------------- ON SUBMIT ----------------
if submit:

    phone_clean = clean_phone(phone)

    if is_valid_phone(phone_clean):

        st.session_state.phone = phone_clean
        st.session_state.submitted = True

        pts, _ = get_user_data(phone_clean)
        st.session_state.points = pts

        st.rerun()

    else:
        st.error("❌ Enter valid number (+91XXXXXXXXXX)")


# ---------------- AFTER SUBMIT ----------------
if st.session_state.submitted:

    pts = st.session_state.points

    # ✅ FIXED MESSAGE
    if pts == 0:
        st.success("👋 Welcome! Start earning rewards 🎉")
    else:
        st.success(f"👋 Welcome back! You have {pts} points")

    # ---------------- PAYMENT ----------------
    if pts < 5 and not st.session_state.paid_clicked:

        st.markdown("### 💸 Get your reward")
        st.link_button("👉 Pay with UPI", UPI_LINK)

        st.caption("💡 Complete payment using any UPI app")
        st.caption("👇 After payment, click below")

        if st.button("✅ I Paid"):

            st.session_state.paid_clicked = True

            new_points = update_points(st.session_state.phone)
            st.session_state.points = new_points

            st.session_state.success_msg = True

            st.rerun()

    # ---------------- SUCCESS ----------------
    if st.session_state.success_msg:

        st.success("🎉 Payment Successful! +1 point added")

        st.markdown(f"""
**at {SHOP_NAME}**

✅ You earned 1 point  
🔥 Complete 5 → get FREE TEA ☕
""")

    # ---------------- REWARDS (ONLY ONCE) ----------------
    if not st.session_state.end_screen:

        points = st.session_state.points

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(points / 5, 1.0))
        st.write(f"🔥 {points}/5 points collected")

        remaining = max(0, 5 - points)

        if remaining > 0:
            st.write(f"🔥 {remaining} more teas to get FREE TEA ☕")
        else:
            st.success("🎉 FREE TEA unlocked!")

    # ---------------- AUTO END SCREEN ----------------
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