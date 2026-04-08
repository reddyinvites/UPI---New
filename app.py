import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Rewards App", layout="centered")

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


# ---------------- SHOPS ----------------
SHOPS = {
    "ravi-tea": {
        "name": "RAVI TEA ☕",
        "tagline": "Morning kick chai 🔥",
        "upi": "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"
    },
    "juice-corner": {
        "name": "JUICE CORNER 🧃",
        "tagline": "Fresh & Healthy 🍊",
        "upi": "upi://pay?pa=yourupi@upi&pn=JuiceCorner&cu=INR"
    }
}

# ---------------- GET SHOP FROM URL ----------------
query = st.query_params

shop_id = query.get("shop", "ravi-tea")

# ⚠️ Important fix (string handling)
if isinstance(shop_id, list):
    shop_id = shop_id[0]

shop = SHOPS.get(shop_id, SHOPS["ravi-tea"])

SHOP_NAME = shop["name"]
TAGLINE = shop["tagline"]
UPI_LINK = shop["upi"]


# ---------------- SESSION ----------------
if "paid" not in st.session_state:
    st.session_state.paid = False

if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = None


# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- FIND ROW ----------------
def find_row(phone):
    phones = sheet.col_values(1)
    for i, val in enumerate(phones):
        if val == phone:
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

    if row:
        current = int(sheet.cell(row, 2).value)
        new_points = current + 1
        sheet.update_cell(row, 2, new_points)
        return new_points
    else:
        sheet.append_row([phone, 1])
        return 1


# ---------------- FRAUD PREVENTION ----------------
def can_click():
    now = datetime.now()

    if st.session_state.last_click_time is None:
        st.session_state.last_click_time = now
        return True

    diff = (now - st.session_state.last_click_time).seconds

    if diff < 10:
        return False
    else:
        st.session_state.last_click_time = now
        return True


# ---------------- UI ----------------
st.markdown(f"## {SHOP_NAME}")
st.caption(TAGLINE)

st.divider()

# ---------------- PAYMENT ----------------
st.link_button("💸 Pay & Earn Rewards", UPI_LINK)
st.caption("After payment, confirm below 👇")

if st.button("✅ I Paid"):

    if not can_click():
        st.error("⛔ Wait few seconds before clicking again")
    else:
        st.session_state.paid = True
        st.balloons()

        st.markdown(f"""
        ### 🎉 Payment Successful!

        **at {SHOP_NAME}**

        ✅ You earned 1 point  
        """)


# ---------------- SAVE + SHOW POINTS ----------------
if st.session_state.paid:

    phone = st.text_input(
        "💾 Save points & get FREE reward 🎁",
        placeholder="+91XXXXXXXXXX"
    )

    if st.button("💾 Save Rewards"):

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number like +919876543210")

        else:
            new_points = update_points(phone)

            st.success(f"🔥 {new_points}/5 points collected")

            st.progress(min(new_points / 5, 1.0))

            st.markdown(f"""
            🎁 Only {max(0, 5 - new_points)} more for FREE reward 🎁
            """)

            if new_points >= 5:
                st.success("🎉 FREE reward unlocked!")

    # show total
    if phone and is_valid_phone(phone):
        current = get_points(phone)

        st.markdown("---")
        st.write(f"🔥 Total: {current}/5 points")
        st.progress(min(current / 5, 1.0))


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")