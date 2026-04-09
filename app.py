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

if "paid_clicked" not in st.session_state:
    st.session_state.paid_clicked = False


# ---------------- CLEAN PHONE ----------------
def clean_phone(p):
    return str(p).strip().replace(" ", "")


# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    phone = clean_phone(phone)
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- FIND ROW ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    phone = clean_phone(phone)

    for i, val in enumerate(phones):
        if clean_phone(val) == phone:
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
    now = datetime.now()

    if row:
        current_points = int(sheet.cell(row, 2).value)
        last_time_str = sheet.cell(row, 3).value

        if last_time_str:
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            if now - last_time < timedelta(hours=2):
                return current_points

        new_points = min(current_points + 1, 5)

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

# ---------------- PHONE INPUT ----------------
phone = st.text_input(
    "📱 Enter your number to check rewards",
    value=st.session_state.phone,
    placeholder="+91XXXXXXXXXX"
)

phone = clean_phone(phone)

if is_valid_phone(phone):
    st.session_state.phone = phone
    st.session_state.points = get_points(phone)


# ---------------- FREE TEA STATE ----------------
if st.session_state.points >= 5:
    st.success("🎉 FREE TEA unlocked!")
    st.markdown("👉 Show this screen to shop owner ☕")

else:
    # ---------------- PAYMENT ----------------
    st.markdown("### 💸 Get your reward")
    st.link_button("👉 Pay with UPI", UPI_LINK)

    st.markdown("💡 Complete payment using any UPI app (GPay / PhonePe / Paytm)")
    st.markdown("👇 After payment, click below to collect your reward")

    # ---------------- PAID BUTTON ----------------
    paid_btn = st.button(
        "✅ I Paid",
        disabled=st.session_state.paid_clicked
    )

    if paid_btn and not st.session_state.paid_clicked:

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number first")
        else:
            st.session_state.paid_clicked = True

            # 🔥 Update points
            new_points = update_points(phone)
            st.session_state.points = new_points

            # 🎉 SUCCESS MESSAGE
            st.success("🎉 Payment Successful! +1 point added")

            st.markdown(f"""
            **at {SHOP_NAME}**

            ✅ You earned 1 point  
            🔥 Complete 5 → get FREE TEA ☕
            """)

            # ⏳ small delay (UX feel)
            time.sleep(2)

            # 🔓 allow next click later
            st.session_state.paid_clicked = False


# ---------------- SHOW REWARDS ----------------
if st.session_state.phone:

    points = st.session_state.points

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(points / 5, 1.0))
    st.write(f"🔥 {points}/5 points collected")

    remaining = max(0, 5 - points)

    if remaining > 0:
        st.markdown(
            f"🔥 {remaining} more tea{'s' if remaining > 1 else ''} to get FREE TEA ☕"
        )
    else:
        st.success("🎉 FREE TEA unlocked!")


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")