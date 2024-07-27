import time

import bcrypt
import extra_streamlit_components as stx
import requests
import streamlit as st

from app_utils import auth


# login page
def login():
    def check_credentials(username: str, password: str) -> bool:
        if st.secrets.auth.get(username):
            return st.secrets.auth.get(username) == password

        return False

    @st.experimental_dialog("Login")
    def login_dialog():
        with st.form("login-form", clear_on_submit=False, border=True):
            username = st.text_input("Username", placeholder="Your username")
            password = st.text_input("Password", type="password", placeholder="Your password")
            submitted = st.form_submit_button("Submit")

            # st.write(st.secrets.auth)
            # st.write(username)
            # st.write(password)

            if submitted:
                if check_credentials(username, password):
                    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    cookie_manager.set("login", f"{username} | {password.decode()}", max_age=3600)
                    time.sleep(1)
                    st.session_state.user = username
                    st.session_state.authentication = True
                    st.rerun()
                else:
                    st.error("Username or password incorrect")
                    st.stop()

    st.image(st.session_state.logo)
    if st.button("Log in", use_container_width=True):
        login_dialog()


# logout page (function)
def logout():
    st.session_state.authentication = False
    try:
        cookie_manager.delete("login")
        time.sleep(2)
        st.rerun()
    except KeyError as e:
        st.warning(e)
        time.sleep(1)
        st.rerun()


def verify_cookies(cookies: dict):
    if not cookies:
        return False
    if len(cookies) <= 2:
        return False

    if cookies.get("login").split(" | ")[0] in st.secrets.auth.keys():
        if bcrypt.checkpw(
            st.secrets.auth.get(cookies.get("login").split(" | ")[0]).encode(),
            cookies.get("login").split(" | ")[1].encode(),
        ):
            return True
    return False


# dashboard_utils
def scrape_icon(url: str = None) -> str | None:
    if not url:
        url = "https://sites.google.com/nypl.org/techconnect/"

    try:
        resp = requests.get(url)
        resp.raise_for_status()

        for line in resp.text.splitlines():
            if 'rel="icon"' in line and 'href="' in line:
                favicon_url = line.split('href="')[-1].split('"')[0]
                return favicon_url

    except requests.exceptions.RequestException as e:
        st.warning(f"Unable to fetch icon: {e}")
        return None


def main() -> None:
    cookies = cookie_manager.get_all()
    if verify_cookies(cookies):
        st.session_state.authentication = True

    if not st.session_state.logo:
        st.session_state.logo = scrape_icon()
    st.logo(st.session_state.logo, icon_image=st.session_state.logo)

    # Router
    login_page = st.Page(
        login,
        title="Log In",
        icon=":material/login:",
        url_path="/login",
        default=(not st.session_state.authentication),
    )
    logout_page = st.Page(logout, title="Log Out", icon=":material/logout:")
    dashboard = st.Page(
        "./dashboard.py",
        title="Dashboard",
        icon=":material/bar_chart:",
        default=(st.session_state.authentication),
    )

    if st.session_state.authentication:
        pg = st.navigation([logout_page, dashboard])
    else:
        pg = st.navigation([st.Page(login)])

    pg.run()


# App Set-up
cookie_manager = stx.CookieManager()

if "authentication" not in st.session_state:
    st.session_state.authentication = False
if "logo" not in st.session_state:
    st.session_state.logo = "./images/TechConnect_logo.png"


if __name__ == "__main__":
    main()
