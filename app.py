import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# ---------------- APP SETTINGS ----------------
st.set_page_config(
    page_title="Ravi Tea",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🔥 Hide Streamlit UI
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 🔥 Mobile full screen feel
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# 🔥 Button style
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 50px;
    font-size: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# 🔥 Splash loading
with st.spinner("Opening Ravi Tea ☕"):
    time.sleep(1)


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
SHOP_NAME = "RAVI TEA"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"


# ---------------- SESSION ----------------
if "phone" not in st.session_state:
    st.session_state.phone = ""

if "points" not in st.session_state:
    st.session_state.points = 0

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
st.markdown(f"""
<div style="text-align:center; padding:10px;">
    <h2>☕ {SHOP_NAME}</h2>
    <p style="color:gray;">🔥 {TAGLINE}</p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ---------------- END SCREEN ----------------
if st.session_state.end_screen:

    st.markdown("""
    ### 🎯 See you again!

    💸 Every tea = reward  
    🎁 Every 5 = FREE tea  

    👉 Come back soon ☕
    """)

    st.caption("Powered by Your Startup 🚀")
    st.stop()


# ---------------- WELCOME ----------------
if not st.session_state.submitted:

    st.markdown("""
    ### ☕ Welcome

    🎁 Earn rewards on every tea  
    💸 Pay easily with UPI  
    """)

    phone = st.text_input("📱 Enter your number", placeholder="+91XXXXXXXXXX")

    if st.button("Continue"):

        phone = clean_phone(phone)

        if is_valid_phone(phone):
            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("Enter valid number")


# ---------------- MAIN FLOW ----------------
if st.session_state.submitted:

    pts = st.session_state.points

    if st.session_state.success_msg:

        st.success("🎉 Payment Successful!")

        st.markdown(f"**+1 Point Added**")

        updated_pts = st.session_state.points

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(updated_pts / 5, 1.0))
        st.write(f"{updated_pts}/5 points")

    else:

        if pts == 0:
            st.success("👋 Welcome!")
        else:
            st.success(f"👋 You have {pts} points")

        if pts < 5:

            st.link_button("💸 Pay Now", UPI_LINK)

            if st.button("✅ I Paid"):
                new_pts = update_points(st.session_state.phone)
                st.session_state.points = new_pts
                st.session_state.success_msg = True
                st.rerun()

        st.divider()
        st.subheader("🎁 Your Rewards")

        st.progress(min(pts / 5, 1.0))
        st.write(f"{pts}/5 points")


# ---------------- RESET ----------------
if st.session_state.success_msg:

    time.sleep(10)

    st.session_state.phone = ""
    st.session_state.points = 0
    st.session_state.success_msg = False
    st.session_state.submitted = False
    st.session_state.end_screen = True

    st.rerun()


# ---------------- FOOTER ----------------
st.caption("Powered by Your Startup 🚀")