import reflex as rx
from app.components.auth_components import signup_card, _auth_layout
from app.state import AuthState


def signup_page() -> rx.Component:
    return _auth_layout(signup_card())