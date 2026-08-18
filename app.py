def show_login():

    left, center, right = st.columns(
        [1, 1.15, 1]
    )

    with center:

        with st.container(
            border=True
        ):

            st.markdown(
                """
                <div class="login-title">
                    Smart Aquaponic Greenhouse
                </div>

                <div class="login-description">
                    Sign in to access the monitoring dashboard
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form(
                "login_form"
            ):

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
