import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

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

if "phone" not in st.session_state:
    st.session_state.phone = ""

if "points" not in st.session_state:
    st.session_state.points = 0


# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- FIND ROW ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if val.strip() == phone.strip():
            return i + 1
    return None


# ---------------- GET DATA ----------------
def get_data(phone):
    row = find_row(phone)
    if row:
        points = int(sheet.cell(row, 2).value)
        last_time = sheet.cell(row, 3).value
        return points, last_time
    return 0, None


# ---------------- UPDATE POINTS WITH COOLDOWN ----------------
def update_points(phone):
    row = find_row(phone)
    now = datetime.now()

    if row:
        current_points = int(sheet.cell(row, 2).value)
        last_time_str = sheet.cell(row, 3).value

        if last_time_str:
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            diff = now - last_time

            # ⛔ COOLDOWN: 2 HOURS
            if diff < timedelta(hours=2):
                remaining = timedelta(hours=2) - diff
                return current_points, False, remaining

        # ✅ ALLOW UPDATE
        new_points = current_points + 1
        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))

        return new_points, True, None

    else:
        # NEW USER
        sheet.append_row([
            phone,
            1,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ])
        return 1, True, None


# ---------------- FRAUD CLICK ----------------
def can_click():
    now = datetime.now()

    if st.session_state.last_click_time is None:
        st.session_state.last_click_time = now
        return True

    diff = (now - st.session_state.last_click_time).seconds

    if diff < 5:
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
        st.error("⛔ Wait few seconds")
    else:
        st.session_state.paid = True
        st.balloons()

        st.markdown(f"""
        ## 🎉 Payment Successful!

        **at {SHOP_NAME}**

        ✅ You earned 1 point  
        🔥 Complete 5 → get FREE TEA ☕
        """)


# ---------------- SAVE ----------------
if st.session_state.paid:

    phone = st.text_input(
        "💾 Save your rewards (WhatsApp number)",
        value=st.session_state.phone,
        placeholder="+91XXXXXXXXXX"
    )

    if st.button("💾 Save Rewards"):

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number")

        else:
            points, allowed, remaining_time = update_points(phone)

            if not allowed:
                mins = int(remaining_time.total_seconds() // 60)
                st.warning(f"⏳ Come back in {mins} mins for next reward ☕")
            else:
                st.session_state.phone = phone
                st.session_state.points = points
                st.rerun()


# ---------------- SHOW REWARDS ----------------
if st.session_state.phone:

    points = st.session_state.points

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(points / 5, 1.0))
    st.write(f"🔥 {points}/5 points collected")

    remaining = max(0, 5 - points)

    if remaining > 0:
        st.markdown(f"🔥 Just {remaining} more tea{'s' if remaining > 1 else ''} to get FREE TEA ☕")
    else:
        st.success("🎉 FREE TEA unlocked!")


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")