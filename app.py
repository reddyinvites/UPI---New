import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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


# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()


# ---------------- DB FUNCTIONS ----------------
def get_points(phone):
    data = sheet.get_all_records()
    for row in data:
        if row["Phone"] == phone:
            return row["Points"]
    return 0


def update_points(phone):
    data = sheet.get_all_records()

    for i, row in enumerate(data):
        if row["Phone"] == phone:
            new_points = row["Points"] + 1
            sheet.update_cell(i + 2, 2, new_points)
            return new_points

    sheet.append_row([phone, 1])
    return 1


# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>
.main {
    background-color: #fff7ed;
}
.title {
    text-align:center;
    font-size:32px;
    font-weight:bold;
}
.tag {
    text-align:center;
    color:gray;
}
.card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
    margin-top:15px;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown(f'<div class="title">{SHOP_NAME}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="tag">{TAGLINE}</div>', unsafe_allow_html=True)

# ---------------- PAYMENT CARD ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("### 💸 Pay & Earn Rewards")

st.link_button("👉 Pay with UPI", UPI_LINK)

st.caption("After payment, confirm below 👇")

# PAYMENT BUTTON
paid_click = st.button("✅ I Paid")

st.markdown('</div>', unsafe_allow_html=True)


# ---------------- SUCCESS FLOW ----------------
if paid_click:
    st.session_state.paid = True

    st.balloons()

    st.markdown(f"""
    <div class="card">
    <h3>🎉 Payment Successful!</h3>
    <p><b>at {SHOP_NAME}</b></p>
    <p>✅ You earned 1 point</p>
    </div>
    """, unsafe_allow_html=True)


# ---------------- PHONE (AFTER REWARD) ----------------
if st.session_state.paid:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    phone = st.text_input(
        "💾 Save your rewards (WhatsApp)",
        placeholder="+91XXXXXXXXXX"
    )

    if phone:

        if not is_valid_phone(phone):
            st.error("❌ Enter valid number like +919876543210")

        else:
            points = update_points(phone)

            st.success(f"🔥 {points}/5 points collected")

            st.progress(min(points / 5, 1.0))

            if points >= 5:
                st.success("🎉 FREE TEA unlocked!")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- FOOTER ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Powered by Your Startup 🚀")