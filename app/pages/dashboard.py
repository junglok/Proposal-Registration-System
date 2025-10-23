import reflex as rx
from app.state import AuthState
from app.components.sidebar import sidebar
from app.components.dashboard_components import (
    dashboard_home,
    create_proposal_form,
    my_proposals_page,
    dashboard_topbar,
    force_password_change_modal,
)
from app.components.admin_components import admin_panel, user_panel


def dashboard_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            dashboard_topbar(),
            force_password_change_modal(),
            rx.el.div(
                rx.match(
                    AuthState.active_page,
                    ("dashboard", dashboard_home()),
                    ("create_proposal", create_proposal_form()),
                    ("my_proposals", my_proposals_page()),
                    ("admin_panel", admin_panel()),
                    ("user_panel", user_panel()),
                    dashboard_home(),
                ),
                class_name="mt-8 space-y-8",
            ),
            class_name=rx.cond(
                AuthState.dark_mode,
                "flex-1 overflow-y-auto p-6 lg:p-10 bg-slate-900/60 text-slate-100 backdrop-blur-xl",
                "flex-1 overflow-y-auto p-6 lg:p-10 bg-white/60 text-slate-900 backdrop-blur",
            ),
        ),
        class_name=rx.cond(
            AuthState.dark_mode,
            "flex min-h-screen w-screen font-['Montserrat'] bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-slate-100",
            "flex min-h-screen w-screen font-['Montserrat'] bg-gradient-to-br from-slate-100 via-white to-slate-50 text-slate-900",
        ),
    )
