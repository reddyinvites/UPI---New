import streamlit as st

st.set_page_config(page_title="Ravi Tea", layout="centered")

# ---------------- SHOP INFO ----------------
SHOP_NAME = "RAVI TEA ☕"
TAGLINE = "Morning kick chai 🔥"

# ---------------- SESSION ----------------
if "points" not in st.session_state:
    st.session_state.points = 0

# ---------------- UI ----------------
st.title(SHOP_NAME)
st.write(TAGLINE)

st.divider()

# ---------------- PAY BUTTON ----------------
upi_link = "upi://pay?pa=yourupi@upi&pn=RaviTea&cu=INR"

if st.button("💸 Pay Now"):
    st.markdown(f"[Click here to Pay]({upi_link})")

st.divider()

# ---------------- AFTER PAYMENT ----------------
if st.button("✅ I Paid"):
    st.session_state.points += 1
    st.success("🎉 Payment Successful!")

    st.markdown(f"""
    **at {SHOP_NAME}**

    ✅ You earned 1 point  
    🔥 Only {5 - st.session_state.points} more for FREE TEA
    """)

# ---------------- LOYALTY ----------------
st.divider()
st.subheader("🎁 Your Rewards")

points = st.session_state.points

boxes = ["✅" if i < points else "⬜" for i in range(5)]
st.write(" ".join(boxes))

st.write(f"{points} / 5 completed")

if points >= 5:
    st.success("🎉 You got FREE TEA!")
