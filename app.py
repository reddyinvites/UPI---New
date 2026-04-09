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
if "points" not in st.session_state:
    st.session_state.points = 0

if "phone" not in st.session_state:
    st.session_state.phone = ""

if "paid_clicked" not in st.session_state:
    st.session_state.paid_clicked = False


# ---------------- HELPERS ----------------
def clean_phone(p):
    return str(p).strip().replace(" ", "")

def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13

def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if clean_phone(val) == phone:
            return i + 1
    return None


def load_user(phone):
    row = find_row(phone)
    if row:
        points = int(sheet.cell(row, 2).value)
        st.session_state.points = points
        st.session_state.phone = phone
    else:
        st.session_state.points = 0
        st.session_state.phone = phone


def update_points(phone):
    row = find_row(phone)
    now = datetime.now()

    if row:
        current = int(sheet.cell(row, 2).value)
        new_points = current + 1

        if new_points > 5:
            new_points = 1

        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))

        return new_points

    else:
        sheet.append_row([phone, 1, now.strftime("%Y-%m-%d %H:%M:%S")])
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

if phone and is_valid_phone(phone):
    load_user(phone)

points = st.session_state.points


# ---------------- FREE TEA MODE ----------------
if points >= 5:

    st.success("🎉 FREE TEA unlocked!")
    st.markdown("👉 Show this screen to shop owner ☕")

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(1.0)
    st.write("🔥 5/5 points collected")

    st.stop()


# ---------------- NORMAL USER ----------------
if phone and is_valid_phone(phone):

    st.markdown("### 💸 Get your reward")

    st.link_button("👉 Pay with UPI", UPI_LINK)

    st.caption("💡 Complete payment using any UPI app (GPay / PhonePe / Paytm)")
    st.caption("👇 After payment, click below to collect your reward")

    if not st.session_state.paid_clicked:

        if st.button("✅ I Paid"):

            st.session_state.paid_clicked = True

            new_points = update_points(phone)
            st.session_state.points = new_points

            # 🎉 SUCCESS MESSAGE
            st.success("🎉 Payment Successful! +1 point added")

            st.markdown(f"""
            **at {SHOP_NAME}**

            ✅ You earned 1 point  
            🔥 Complete 5 → get FREE TEA ☕
            """)

            # 🔊 SOUND
            st.markdown("""
            <audio autoplay>
              <source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)

            # 🎊 CONFETTI
            st.markdown("""
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <script>
            confetti({
                particleCount: 120,
                spread: 90,
                origin: { y: 0.6 }
            });
            </script>
            """, unsafe_allow_html=True)

            # ⏳ WAIT (no instant rerun)
            time.sleep(3)

            # 🔄 RESET BUTTON (no rerun)
            st.session_state.paid_clicked = False


# ---------------- REWARDS DISPLAY ----------------
if phone:

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(points / 5, 1.0))
    st.write(f"🔥 {points}/5 points collected")

    if points < 5:
        st.markdown(f"🔥 {5 - points} more teas to get FREE TEA ☕")


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")