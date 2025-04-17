# Author: Tumu Lakshman Prasanna Kumar
# Email: lpkumartumu@gmail.com
# GitHub: https://github.com/lakshman200309
# LinkedIn: https://www.linkedin.com/in/tumu-lakshman-prasanna-kumar-a37561270
# Portfolio: https://lakshman200309.github.io/Personal_Portfolio/

import streamlit as st
import enroll
import login

st.set_page_config(page_title="Face Authentication App", layout="centered")

# Initialize session state
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
if "distance" not in st.session_state:
    st.session_state.distance = None

st.title("🔐 Face Authentication System")

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Author Info**")
st.sidebar.markdown(
    "**Tumu Lakshman Prasanna Kumar**  \n"
    "📧 [Email](mailto:lpkumartumu@gmail.com)  \n"
    "🐙 [GitHub](https://github.com/lakshman200309)  \n"
    "🔗 [LinkedIn](https://www.linkedin.com/in/tumu-lakshman-prasanna-kumar-a37561270)  \n"
    "🌐 [Portfolio](https://lakshman200309.github.io/Personal_Portfolio/)"
)

# ----------------- MENU -----------------
menu = st.sidebar.selectbox("Choose Option", ["Enroll", "Login", "Welcome Page", "About"])

# ----------------- Enroll Section -----------------
if menu == "Enroll":
    st.subheader("📝 Enroll User by ID")
    user_id = st.text_input("Enter your User ID")
    if st.button("Start Face Enrollment"):
        if user_id:
            with st.spinner("Enrolling user..."):
                enroll.enroll_user(user_id)
                st.success(f"Enrollment complete for ID: {user_id}")
        else:
            st.warning("Please enter a valid User ID.")

# ----------------- Login Section -----------------
elif menu == "Login":
    st.subheader("🔓 Login with Face")
    if st.button("Start Face Authentication"):
        with st.spinner("Authenticating..."):
            result = login.authenticate_face()
            if result.startswith("Authenticated"):
                try:
                    # Parse ID and distance
                    prefix, dist_part = result.split(" (distance: ")
                    user_id = prefix.split("ID: ")[1].strip()
                    distance = float(dist_part.replace(")", ""))

                    # Save to session state
                    st.session_state.authenticated_user = user_id
                    st.session_state.distance = distance

                    st.success(result)
                    st.info("Now go to the 'Welcome Page' from the sidebar.")
                except Exception as e:
                    st.error(f"⚠️ Error parsing authentication result: {e}")
            else:
                st.error(result)

# ----------------- Welcome Page -----------------
elif menu == "Welcome Page":
    st.subheader("🎉 Welcome Page")

    if st.session_state.authenticated_user:
        st.success(f"Welcome, ID: {st.session_state.authenticated_user}")
        st.write(f"✅ Authentication confidence (lower is better): `{st.session_state.distance:.2f}`")

        st.markdown("---")
        st.markdown("👨‍💻 **Author**: [Tumu Lakshman Prasanna Kumar](https://lakshman200309.github.io/Personal_Portfolio/)")

        st.balloons()

        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.authenticated_user = None
            st.session_state.distance = None
            st.success("You have been logged out.")
    else:
        st.warning("⚠️ Please login first to access the welcome page.")

# ----------------- About Page -----------------
elif menu == "About":
    st.subheader("👨‍💻 About the Author")
    st.markdown("""
        **Tumu Lakshman Prasanna Kumar**  
        📧 [lpkumartumu@gmail.com](mailto:lpkumartumu@gmail.com)  
        🐙 [GitHub](https://github.com/lakshman200309)  
        🔗 [LinkedIn](https://www.linkedin.com/in/tumu-lakshman-prasanna-kumar-a37561270)  
        🌐 [Portfolio](https://lakshman200309.github.io/Personal_Portfolio/)
    """)
