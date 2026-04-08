import streamlit as st

st.set_page_config(page_title="Tea Loyalty", layout="centered")

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"
UPI_LINK = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

# ---------------- SESSION ----------------
if "points" not in st.session_state:
    st.session_state.points = 0

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
.big-title {
    font-size: 32px;
    font-weight: bold;
}
.tagline {
    color: gray;
    font-size: 16px;
}
.center {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(f'<div class="center big-title">{SHOP_NAME}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="center tagline">{TAGLINE}</div>', unsafe_allow_html=True)

st.divider()

# ---------------- PHONE INPUT ----------------
phone = st.text_input("📱 Enter your phone number to earn points")

st.divider()

# ---------------- PAY BUTTON ----------------
st.link_button("💸 Pay with UPI", UPI_LINK)

st.write("👇 After payment, click below")

# ---------------- PAYMENT CONFIRM ----------------
if st.button("✅ I Paid"):
    if phone == "":
        st.warning("Please enter phone number first!")
    else:
        st.session_state.points += 1

        st.balloons()

        st.markdown(f"""
        ## 🎉 Payment Successful!

        ### at {SHOP_NAME}

        ✅ You earned 1 point  
        🔥 Only {5 - st.session_state.points} more for FREE TEA ☕
        """)

# ---------------- LOYALTY ----------------
st.divider()
st.subheader("🎁 Your Rewards")

points = st.session_state.points

# Progress bar
progress = min(points / 5, 1.0)
st.progress(progress)

st.write(f"🔥 {points}/5 points collected")

# Free reward
if points >= 5:
    st.success("🎉 You got FREE TEA! Show this to shop owner.")

# ---------------- FOOTER ----------------
st.divider()
st.caption("Powered by Your Startup 🚀")