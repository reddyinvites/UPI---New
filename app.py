import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Tea Loyalty", layout="centered")

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


# ---------------- HELPERS ----------------
def clean_phone(phone):
    return phone.strip()

def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


def get_data(phone):
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if clean_phone(row["Phone"]) == clean_phone(phone):
            return row["Points"], row.get("LastTime", ""), i + 2
    return 0, "", None


def update_points(phone):
    points, _, row = get_data(phone)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if row:
        new_points = points + 1
        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now)
        return new_points
    else:
        sheet.append_row([phone, 1, now])
        return 1


def reset_points(phone):
    _, _, row = get_data(phone)
    if row:
        sheet.update_cell(row, 2, 0)


# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)
st.divider()

st.subheader("💸 Pay & Earn Rewards")

st.link_button("👉 Pay with UPI", UPI_LINK)
st.write("👇 After payment, confirm below")

if st.button("✅ I Paid"):
    st.success("🎉 Payment Successful!")
    st.write(f"at {SHOP_NAME}")
    st.write("✅ You earned 1 point")

# ---------------- PHONE ----------------
phone = st.text_input(
    "💾 Save points & get FREE tea 🎁",
    placeholder="+91XXXXXXXXXX"
)

phone_clean = clean_phone(phone)


# ---------------- SAVE LOGIC ----------------
if phone and is_valid_phone(phone_clean):

    current_points, last_time, _ = get_data(phone_clean)

    show_button = True
    cooldown_active = False

    # 🔒 Cooldown check (2 hours)
    if last_time:
        last_time_dt = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last_time_dt

        if diff < timedelta(hours=2):
            mins = int((timedelta(hours=2) - diff).total_seconds() // 60)

            # update UI state
            st.session_state.phone = phone_clean
            st.session_state.points = current_points

            st.warning(f"⏳ Come back in {mins} mins for next reward ☕")

            show_button = False
            cooldown_active = True

    # ❌ stop if already 5 points
    if current_points >= 5:
        show_button = False

    # ---------------- SAVE BUTTON ----------------
    if show_button:
        if st.button("💾 Save Rewards"):
            new_points = update_points(phone_clean)

            st.session_state.phone = phone_clean
            st.session_state.points = new_points

            st.success("🔥 Points added!")

    # ---------------- REWARDS DISPLAY ----------------
    if st.session_state.phone == phone_clean:
        points = st.session_state.points
    else:
        points = current_points

    st.divider()
    st.subheader("🎁 Your Rewards")

    st.progress(min(points / 5, 1.0))
    st.write(f"🔥 {points}/5 points collected")

    remaining = 5 - points

    if points < 5:
        st.write(f"🔥 Just {remaining} more tea to get FREE TEA ☕")

    # ---------------- REDEEM ----------------
    if points >= 5:
        st.success("🎉 FREE TEA READY! Show to shop ☕")

        if st.button("🎁 Redeem Free Tea"):
            reset_points(phone_clean)
            st.session_state.points = 0
            st.success("✅ Redeemed! Points reset to 0")

# ---------------- FOOTER ----------------
st.write("Powered by Your Startup 🚀")