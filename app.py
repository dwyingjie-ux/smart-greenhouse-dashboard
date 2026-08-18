import streamlit as st


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Smart Aquaponic Greenhouse",
    page_icon="🌱",
    layout="centered"
)


# =========================================================
# LOGIN DETAILS
# =========================================================

LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin"


# =========================================================
# LOGIN SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🌱 Smart Aquaponic Greenhouse")

    st.write("Please login to access the dashboard.")


    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True
        )


    if login_button:

        if (
            username == LOGIN_USERNAME
            and
            password == LOGIN_PASSWORD
        ):

            st.session_state.logged_in = True

            st.rerun()

        else:

            st.error(
                "Incorrect username or password."
            )


# =========================================================
# AFTER LOGIN
# =========================================================

else:

    st.success(
        "Login successful!"
    )

    st.title(
        "Smart Aquaponic Greenhouse Dashboard"
    )

    st.write(
        "Dashboard will appear here."
    )


    if st.button(
        "Logout"
    ):

        st.session_state.logged_in = False

        st.rerun()
