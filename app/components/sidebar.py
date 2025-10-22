import reflex as rx
from app.state import AuthState


def _nav_item(icon: str, text: str, page: str) -> rx.Component:
    return rx.el.a(
        rx.icon(tag=icon, class_name="h-5 w-5"),
        rx.el.span(text, class_name="font-medium"),
        on_click=lambda: AuthState.set_active_page(page),
        class_name=rx.cond(
            AuthState.active_page == page,
            "flex items-center gap-3 rounded-lg bg-teal-100 px-3 py-2 text-teal-800 transition-all hover:text-teal-900 cursor-pointer",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-600 transition-all hover:bg-gray-100 hover:text-gray-900 cursor-pointer",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("file-text", class_name="h-8 w-8 text-teal-500"),
                    rx.el.h1(
                        "[GSDC TEM 활용지원 프로그램] 활용계획서 제출",
                        class_name="text-sm font-bold tracking-tight text-gray-800",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-24 items-center border-b px-6 text-center",
            ),
            rx.el.nav(
                _nav_item("home", "Dashboard", "dashboard"),
                _nav_item("circle_plus", "Create Proposal", "create_proposal"),
                _nav_item("list", "My Proposals", "my_proposals"),
                rx.cond(
                    AuthState.is_admin,
                    _nav_item("shield", "Admin Panel", "admin_panel"),
                    None,
                ),
                class_name="grid items-start px-4 text-sm font-medium",
            ),
            class_name="flex-1 overflow-auto py-2",
        ),
        rx.el.div(
            _nav_item("log-out", "Logout", "logout"),
            on_click=AuthState.logout,
            class_name="mt-auto p-4 border-t",
        ),
        class_name="hidden border-r bg-white md:flex md:flex-col min-h-screen w-64 shrink-0",
    )