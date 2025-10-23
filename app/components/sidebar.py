import reflex as rx
from app.state import AuthState
from app.states.proposal_state import ProposalState


def _nav_item(
    icon: str, text: str, page: str, on_click=None
) -> rx.Component:
    handler = on_click or (lambda: AuthState.set_active_page(page))
    icon_class = rx.cond(
        AuthState.dark_mode,
        "h-5 w-5 text-slate-200",
        "h-5 w-5 text-slate-600",
    )
    active_class = rx.cond(
        AuthState.dark_mode,
        "flex items-center gap-3 rounded-2xl bg-white/15 px-3 py-2 text-white shadow-lg transition hover:bg-white/20 cursor-pointer",
        "flex items-center gap-3 rounded-2xl bg-teal-100/90 px-3 py-2 text-teal-800 shadow-sm transition hover:bg-teal-100 cursor-pointer",
    )
    inactive_class = rx.cond(
        AuthState.dark_mode,
        "flex items-center gap-3 rounded-2xl px-3 py-2 text-slate-300 transition hover:bg-white/10 hover:text-white cursor-pointer",
        "flex items-center gap-3 rounded-2xl px-3 py-2 text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 cursor-pointer",
    )
    return rx.el.a(
        rx.icon(tag=icon, class_name=icon_class),
        rx.el.span(
            text,
            class_name=rx.cond(
                AuthState.dark_mode,
                "font-medium text-sm",
                "font-medium text-sm",
            ),
        ),
        on_click=handler,
        class_name=rx.cond(AuthState.active_page == page, active_class, inactive_class),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "sparkles",
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "h-8 w-8 text-cyan-400",
                            "h-8 w-8 text-cyan-500",
                        ),
                    ),
                    rx.el.div(
                        rx.el.span(
                            "Signed in as",
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "text-xs uppercase tracking-wide text-slate-400",
                                "text-xs uppercase tracking-wide text-slate-500",
                            ),
                        ),
                        rx.el.span(
                            AuthState.authenticated_user,
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "text-sm font-semibold text-white truncate",
                                "text-sm font-semibold text-slate-800 truncate",
                            ),
                        ),
                        class_name="flex flex-col text-left",
                    ),
                    class_name="flex items-center gap-3",
                ),
                class_name="flex h-24 items-center border-b border-white/10 px-6",
            ),
            rx.el.nav(
                _nav_item("home", "Dashboard", "dashboard"),
                _nav_item(
                    "circle_plus",
                    "Create Proposal",
                    "create_proposal",
                    ProposalState.start_new_proposal,
                ),
                _nav_item("list", "My Proposals", "my_proposals"),
                rx.cond(
                    AuthState.is_admin,
                    rx.fragment(
                        _nav_item("shield", "Admin Panel", "admin_panel"),
                        _nav_item("users", "User Panel", "user_panel"),
                    ),
                    None,
                ),
                class_name="grid items-start px-4 text-sm font-medium gap-2",
            ),
            class_name="flex-1 overflow-auto py-2",
        ),
        rx.el.div(
            _nav_item("log-out", "Logout", "logout"),
            on_click=AuthState.logout,
            class_name="mt-auto p-4 border-t border-white/10",
        ),
        class_name=AuthState.sidebar_classes,
    )
