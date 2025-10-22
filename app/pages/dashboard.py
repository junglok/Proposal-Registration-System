import reflex as rx
from app.state import AuthState
from app.components.sidebar import sidebar
from app.components.dashboard_components import (
    dashboard_home,
    create_proposal_form,
    my_proposals_page,
)
from app.components.admin_components import admin_panel


def dashboard_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.match(
                AuthState.active_page,
                ("dashboard", dashboard_home()),
                ("create_proposal", create_proposal_form()),
                ("my_proposals", my_proposals_page()),
                ("admin_panel", admin_panel()),
                dashboard_home(),
            ),
            class_name="flex-1 p-6 lg:p-8 bg-gray-50 overflow-y-auto",
        ),
        class_name="flex min-h-screen w-screen font-['Montserrat']",
    )