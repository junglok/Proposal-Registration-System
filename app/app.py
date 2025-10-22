import reflex as rx
from app.pages.signup import signup_page
from app.pages.signin import signin_page
from app.pages.dashboard import dashboard_page
from app.state import AuthState


@rx.page(on_load=AuthState.check_auth)
def protected_dashboard() -> rx.Component:
    return dashboard_page()


def index() -> rx.Component:
    return rx.cond(AuthState.is_authenticated, protected_dashboard(), signin_page())


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)
app.add_page(signup_page, route="/signup")
app.add_page(signin_page, route="/signin")
app.add_page(protected_dashboard, route="/dashboard")