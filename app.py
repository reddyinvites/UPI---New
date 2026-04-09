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

# ✅ NEW (brand screen control)
if "show_brand_only" not in st.session_state:
    st.session_state.show_brand_only = True


# ---------------- CLEAN PHONE ----------------
def clean_phone(p):
    return str(p).strip().replace(" ", "")


def is_valid_phone(phone):
    phone = clean_phone(phone)
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- FIND ROW ----------------
def find_row(phone):
    phone = clean_phone(phone)
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
    phone = clean_phone(phone)
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


# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)

st.divider()


# ---------------- BRAND SCREEN ----------------
if st.session_state.show_brand_only:

    st.markdown("""
    ### ☕ Welcome to RAVI TEA

    🔥 Fresh chai. Every time  
    💸 Pay easily with UPI  
    🎁 Earn rewards & get FREE tea  

    👇 Enter your number to continue
    """)


# ---------------- PHONE INPUT ----------------
phone = st.text_input(
    "📱 Enter your number to check rewards",
    value=st.session_state.phone,
    placeholder="+91XXXXXXXXXX",
    disabled=st.session_state.paid_clicked
)

phone_clean = clean_phone(phone)

if is_valid_phone(phone_clean):

    st.session_state.phone = phone_clean
    st.session_state.show_brand_only = False  # ✅ hide brand screen

    pts, last = get_user_data(phone_clean)
    st.session_state.points = pts

    if not st.session_state.paid_clicked:

        if pts >= 5:
            st.success("🎉 FREE TEA unlocked!")
            st.markdown("👉 Show this screen to shop owner ☕")

        else:
            st.markdown("### 💸 Get your reward")
            st.link_button(
                "👉 Pay with UPI",
                UPI_LINK,
                disabled=st.session_state.paid_clicked
            )

            st.caption("💡 Complete payment using any UPI app (GPay / PhonePe / Paytm)")
            st.caption("👇 After payment, click below to collect your reward")

            paid_btn = st.button(
                "✅ I Paid",
                disabled=st.session_state.paid_clicked
            )

            if paid_btn and not st.session_state.paid_clicked:

                st.session_state.paid_clicked = True

                new_points = update_points(phone_clean)
                st.session_state.points = new_points

                st.session_state.success_msg = True

                st.rerun()


# ---------------- SUCCESS MESSAGE ----------------
if st.session_state.success_msg:
    st.success("🎉 Payment Successful! +1 point added")

    st.markdown(f"""
    **at {SHOP_NAME}**

    ✅ You earned 1 point  
    🔥 Complete 5 → get FREE TEA ☕
    """)


# ---------------- SHOW REWARDS ----------------
if st.session_state.phone:

    points = st.session_state.points

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(points / 5, 1.0))
    st.write(f"🔥 {points}/5 points collected")

    remaining = max(0, 5 - points)

    if remaining > 0:
        st.markdown(f"🔥 {remaining} more tea{'s' if remaining > 1 else ''} to get FREE TEA ☕")
    else:
        st.success("🎉 FREE TEA unlocked!")


# ---------------- AUTO RESET ----------------
if st.session_state.success_msg:

    time.sleep(6)

    st.session_state.phone = ""
    st.session_state.points = 0
    st.session_state.paid_clicked = False
    st.session_state.success_msg = False
    st.session_state.show_brand_only = True  # ✅ back to brand screen

    st.rerun()


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")