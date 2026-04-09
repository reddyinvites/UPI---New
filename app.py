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
for key, default in {
    "phone": "",
    "points": 0,
    "paid_clicked": False,
    "success_msg": False,
    "submitted": False,
    "end_screen": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


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
        return int(sheet.cell(row, 2).value or 0)
    return 0


# ---------------- COOLDOWN ----------------
def update_points(phone):
    row = find_row(phone)
    now = datetime.now()
    COOLDOWN_HOURS = 3

    if row:
        current_points = int(sheet.cell(row, 2).value or 0)
        last_time_str = sheet.cell(row, 3).value

        if last_time_str:
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            diff = now - last_time

            if diff < timedelta(hours=COOLDOWN_HOURS):
                remaining = timedelta(hours=COOLDOWN_HOURS) - diff
                return current_points, False, remaining

        new_points = current_points + 1
        sheet.update_cell(row, 2, new_points)
        sheet.update_cell(row, 3, now.strftime("%Y-%m-%d %H:%M:%S"))

        return new_points, True, None

    else:
        sheet.append_row([phone, 1, now.strftime("%Y-%m-%d %H:%M:%S")])
        return 1, True, None


# ---------------- HEADER ----------------
st.markdown(f"## {SHOP_NAME}")
st.write(TAGLINE)
st.divider()


# ---------------- WELCOME ----------------
if not st.session_state.submitted:

    st.markdown("""
### ☕ Welcome to RAVI TEA

🔥 Morning kick chai that boosts your day  
💸 Pay easily with UPI  
🎁 Earn rewards on every tea  
☕ Complete 5 → Get 1 FREE  
👇 Enter your number
""")

    with st.form("form"):
        phone = st.text_input("📱 Enter your number", "+91XXXXXXXXXX")
        submit = st.form_submit_button("Check")

    if submit:
        phone = clean_phone(phone)

        if is_valid_phone(phone):
            st.session_state.phone = phone
            st.session_state.points = get_user_data(phone)
            st.session_state.submitted = True
            st.rerun()
        else:
            st.error("Invalid number")


# ---------------- MAIN ----------------
if st.session_state.submitted:

    phone = st.session_state.phone
    pts = st.session_state.points

    if st.session_state.success_msg:

        st.success("🎉 Payment Successful! +1 point")

        st.progress(min(pts / 5, 1.0))
        st.write(f"{pts}/5 points")

        if pts >= 5:
            st.success("🎉 FREE TEA!")
            st.balloons()

        time.sleep(5)

        for k in ["phone","points","success_msg","submitted"]:
            st.session_state[k] = False if isinstance(st.session_state[k], bool) else ""

        st.rerun()

    if pts < 5:

        st.link_button("💸 Pay with UPI", UPI_LINK)

        if st.button("✅ I Paid"):
            new_pts, allowed, remaining = update_points(phone)

            if not allowed:
                mins = int(remaining.total_seconds() // 60)
                st.warning(f"Wait {mins} mins")
            else:
                st.session_state.points = new_pts
                st.session_state.success_msg = True
                st.rerun()

    else:
        st.success("🎉 FREE TEA unlocked!")


# ---------------- SIMPLE DASHBOARD ----------------
st.sidebar.title("🔐 Owner Panel")

ADMIN_PASSWORD = "1234"
admin_pass = st.sidebar.text_input("Password", type="password")

if admin_pass == ADMIN_PASSWORD:

    st.sidebar.success("Logged in")

    data = sheet.get_all_values()  # 🔥 FIXED

    total_users = len(data) - 1  # exclude header

    total_points = 0
    today_visits = 0
    today = datetime.now().date()

    for row in data[1:]:
        try:
            pts = int(row[1])
            total_points += pts

            if row[2]:
                last = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S").date()
                if last == today:
                    today_visits += 1
        except:
            pass

    TEA_PRICE = 10
    revenue = today_visits * TEA_PRICE

    st.markdown("### 📊 Dashboard")
    st.write(f"👥 Users: {total_users}")
    st.write(f"🎯 Total Points: {total_points}")
    st.write(f"🔥 Today Visits: {today_visits}")
    st.write(f"💰 Today Revenue: ₹{revenue}")

else:
    st.sidebar.info("Enter password")