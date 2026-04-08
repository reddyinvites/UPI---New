import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="RAVI TEA ☕", layout="centered")

st.title("RAVI TEA ☕")
st.caption("Morning kick chai 🔥")

# ---------------- GOOGLE SHEETS ----------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key("YOUR_SHEET_ID").sheet1


# ---------------- HELPERS ----------------

def normalize(phone):
    return phone.replace("+91", "").replace(" ", "").strip()


def get_user_row(phone):
    data = sheet.get_all_records()

    for i, row in enumerate(data):
        if normalize(str(row["Phone"])) == normalize(str(phone)):
            return i + 2, row  # row index + header

    return None, None


def get_points(phone):
    _, row = get_user_row(phone)
    if row:
        return int(row.get("Points", 0))
    return 0


def update_points(phone, new_points):
    row_index, _ = get_user_row(phone)

    if row_index:
        sheet.update_cell(row_index, 2, new_points)
        sheet.update_cell(row_index, 3, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        sheet.append_row([
            phone,
            new_points,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])


def get_last_time(phone):
    _, row = get_user_row(phone)
    if row and row.get("LastTime"):
        return datetime.strptime(row["LastTime"], "%Y-%m-%d %H:%M:%S")
    return None


# ---------------- UI ----------------

phone = st.text_input("📱 Enter your number", placeholder="+91XXXXXXXXXX")

st.markdown("## 💸 Pay & Earn Rewards")
st.button("👉 Pay with UPI")

paid = st.button("✅ I Paid")

# ---------------- LOGIC ----------------

if phone:

    points = get_points(phone)
    last_time = get_last_time(phone)

    cooldown_minutes = 30

    allow = True
    remaining = 0

    if last_time:
        diff = datetime.now() - last_time
        if diff < timedelta(minutes=cooldown_minutes):
            allow = False
            remaining = int((timedelta(minutes=cooldown_minutes) - diff).total_seconds() // 60)

    # 🎁 FREE TEA MODE
    if points >= 5:
        st.success("🎉 FREE TEA unlocked!")
        st.info("👉 Show this screen to shop owner ☕")

        st.markdown("## 🎁 Your Rewards")
        st.progress(1.0)
        st.success("🔥 5/5 points collected")

    else:

        # ---------------- PAYMENT ----------------
        if paid:

            if not allow:
                st.warning(f"⏳ Come back in {remaining} mins for next reward ☕")

            else:
                points += 1
                update_points(phone, points)

                st.success("🎉 Payment Successful!")
                st.write("✅ You earned 1 point")

                if points >= 5:
                    st.success("🔥 Completed 5 → get FREE TEA ☕")
                else:
                    st.info(f"🔥 Only {5 - points} more for FREE TEA ☕")

        # ---------------- REWARDS ----------------
        points = get_points(phone)  # refresh

        st.markdown("## 🎁 Your Rewards")

        progress = min(points / 5, 1.0)
        st.progress(progress)

        st.write(f"🔥 {points}/5 points collected")

        if points < 5:
            st.write(f"🔥 Just {5 - points} more teas to get FREE TEA ☕")