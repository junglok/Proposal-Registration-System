import reflex as rx
from app.components.auth_components import signin_card, _auth_layout
from app.state import AuthState


def signin_page() -> rx.Component:
    return _auth_layout(signin_card())