import streamlit as st

st.set_page_config(page_title="Tea Loyalty", layout="centered")

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

# ---------------- SESSION ----------------
if "points" not in st.session_state:
    st.session_state.points = 0

if "paid" not in st.session_state:
    st.session_state.paid = False

if "saved" not in st.session_state:
    st.session_state.saved = False

# ---------------- VALIDATION ----------------
def is_valid_phone(phone):
    return phone.startswith("+91") and len(phone) == 13 and phone[3:].isdigit()

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.big-title {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
}
.tagline {
    color: gray;
    text-align: center;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(f'<div class="big-title">{SHOP_NAME}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="tagline">{TAGLINE}</div>', unsafe_allow_html=True)

st.divider()

# ---------------- PAY ----------------
st.link_button("💸 Pay with UPI", UPI_LINK)

st.write("👇 After payment, click below")

# ---------------- PAYMENT BUTTON ----------------
if st.button("✅ I Paid") and not st.session_state.paid:
    st.session_state.points += 1
    st.session_state.paid = True
    st.balloons()

# ---------------- AUTO SUCCESS DISPLAY ----------------
if st.session_state.paid:
    st.markdown(f"""
    ## 🎉 Payment Successful!

    ### at {SHOP_NAME}

    ✅ You earned 1 point  
    🔥 Only {5 - st.session_state.points} more for FREE TEA ☕
    """)

    # ---------------- SAVE NUMBER ----------------
    if not st.session_state.saved:
        phone = st.text_input("💾 Save your rewards (Enter WhatsApp number)", placeholder="+91XXXXXXXXXX")

        if phone:
            if is_valid_phone(phone):
                st.success("✅ Rewards saved!")
                st.session_state.saved = True
            else:
                st.error("❌ Enter valid number like +919876543210")

# ---------------- LOYALTY ----------------
st.divider()
st.subheader("🎁 Your Rewards")

points = st.session_state.points
progress = min(points / 5, 1.0)

st.progress(progress)
st.write(f"🔥 {points}/5 points collected")

# ---------------- FREE REWARD ----------------
if points >= 5:
    st.success("🎉 You got FREE TEA! Show this to shop owner.")

# ---------------- RESET (FOR TESTING) ----------------
st.divider()
if st.button("🔄 Reset (for demo)"):
    st.session_state.points = 0
    st.session_state.paid = False
    st.session_state.saved = False

# ---------------- FOOTER ----------------
st.caption("Powered by Your Startup 🚀")