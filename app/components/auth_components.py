import reflex as rx
from app.state import AuthState
from typing import Optional


def _input_field(
    icon_tag: str,
    placeholder: str,
    field_type: str,
    value: rx.Var[str],
    error: rx.Var[Optional[str]],
    on_change: rx.event.EventHandler,
) -> rx.Component:
    icon_class = rx.cond(
        AuthState.dark_mode,
        "h-5 w-5 text-slate-300",
        "h-5 w-5 text-slate-400",
    )
    base_class = rx.cond(
        AuthState.dark_mode,
        "block w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-3 text-sm text-slate-100 placeholder:text-slate-400 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
        "block w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-900 placeholder:text-slate-400 transition focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
    )
    error_class = rx.cond(
        AuthState.dark_mode,
        "block w-full rounded-xl border border-red-400 bg-red-900/40 py-2.5 pl-10 pr-3 text-sm text-red-100 placeholder:text-red-200 transition focus:border-red-400 focus:outline-none focus:ring-2 focus:ring-red-400/30",
        "block w-full rounded-xl border border-red-300 bg-red-50 py-2.5 pl-10 pr-3 text-sm text-red-900 placeholder:text-red-400 transition focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30",
    )
    error_text = rx.cond(
        AuthState.dark_mode,
        "mt-2 text-xs text-red-300",
        "mt-2 text-xs text-red-600",
    )
    return rx.el.div(
        rx.el.div(
            rx.icon(tag=icon_tag, class_name=icon_class),
            class_name="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3",
        ),
        rx.el.input(
            placeholder=placeholder,
            type=field_type,
            default_value=value,
            on_change=on_change,
            class_name=rx.cond(error, error_class, base_class),
        ),
        rx.cond(error, rx.el.p(error, class_name=error_text), None),
        class_name="relative",
    )


def _auth_button(
    text: str, is_valid: rx.Var[bool], on_click: rx.event.EventHandler
) -> rx.Component:
    return rx.el.button(
        rx.cond(AuthState.loading, rx.spinner(class_name="h-5 w-5 text-white"), text),
        on_click=on_click,
        disabled=~is_valid | AuthState.loading,
        class_name=rx.cond(
            AuthState.dark_mode,
            "flex w-full items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-5 py-2.5 text-sm font-semibold text-slate-900 shadow-xl transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40 disabled:cursor-not-allowed disabled:opacity-60",
            "flex w-full items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xl transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40 disabled:cursor-not-allowed disabled:opacity-60",
        ),
    )


def _auth_card(
    title: str,
    *children,
    toggle_text: str,
    toggle_link_text: str,
    toggle_link_href: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "file-text",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "h-8 w-8 text-cyan-400 drop-shadow",
                    "h-8 w-8 text-cyan-500",
                ),
            ),
            rx.el.h1(
                "GSDC TEM Data Computing",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-xl font-bold tracking-tighter text-white text-center",
                    "text-xl font-bold tracking-tighter text-slate-900 text-center",
                ),
            ),
            class_name="mb-6 flex flex-col items-center justify-center gap-2",
        ),
        rx.el.div(
            rx.el.h2(
                title,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-xl font-semibold text-white",
                    "text-xl font-semibold text-slate-900",
                ),
            ),
            rx.el.div(*children, class_name="mt-6 space-y-4"),
            class_name="w-full",
        ),
        rx.el.p(
            toggle_text,
            " ",
            rx.el.a(
                toggle_link_text,
                href=toggle_link_href,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "font-medium text-cyan-300 hover:underline",
                    "font-medium text-teal-600 hover:underline",
                ),
            ),
            class_name=rx.cond(
                AuthState.dark_mode,
                "mt-6 text-center text-sm text-slate-300",
                "mt-6 text-center text-sm text-slate-600",
            ),
        ),
        class_name=rx.cond(
            AuthState.dark_mode,
            "flex w-full max-w-sm flex-col items-center rounded-3xl border border-white/10 bg-white/10 p-8 shadow-2xl backdrop-blur",
            "flex w-full max-w-sm flex-col items-center rounded-3xl border border-white/60 bg-white p-8 shadow-xl backdrop-blur",
        ),
    )


def signin_card() -> rx.Component:
    return _auth_card(
        "Sign in to your account",
        _input_field(
            "mail",
            "your.email@example.com",
            "email",
            AuthState.email,
            AuthState.email_error,
            AuthState.on_email_change,
        ),
        _input_field(
            "lock",
            "••••••••",
            "password",
            AuthState.password,
            AuthState.password_error,
            AuthState.on_password_change,
        ),
        rx.el.div(
            rx.el.button(
                "Forgot password?",
                on_click=AuthState.open_password_reset_modal,
                type="button",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-sm font-semibold text-cyan-300 hover:text-cyan-200 transition",
                    "text-sm font-semibold text-teal-600 hover:text-teal-500 transition",
                ),
            ),
            class_name="flex items-center justify-end",
        ),
        _auth_button(
            "Sign In", AuthState.is_signin_form_valid, AuthState.handle_signin
        ),
        toggle_text="Don't have an account?",
        toggle_link_text="Sign up",
        toggle_link_href="/signup",
    )


def signup_card() -> rx.Component:
    return _auth_card(
        "Create a new account",
        _input_field(
            "mail",
            "your.email@example.com",
            "email",
            AuthState.email,
            AuthState.email_error,
            AuthState.on_email_change,
        ),
        _input_field(
            "lock",
            "Create a password",
            "password",
            AuthState.password,
            AuthState.password_error,
            AuthState.on_password_change,
        ),
        _input_field(
            "lock",
            "Confirm your password",
            "password",
            AuthState.confirm_password,
            AuthState.confirm_password_error,
            [AuthState.on_confirm_password_change, AuthState.set_page("signup")],
        ),
        _auth_button(
            "Create Account", AuthState.is_signup_form_valid, AuthState.handle_signup
        ),
        toggle_text="Already have an account?",
        toggle_link_text="Sign in",
        toggle_link_href="/signin",
    )


def _auth_layout(card: rx.Component) -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        tag=rx.cond(AuthState.dark_mode, "sun", "moon"),
                        class_name="h-4 w-4",
                    ),
                    on_click=AuthState.toggle_dark_mode,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "inline-flex items-center justify-center rounded-full border border-white/20 bg-white/10 p-2 text-white transition hover:bg-white/20",
                        "inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2 text-slate-700 transition hover:bg-slate-100",
                    ),
                ),
                card,
                class_name="flex flex-col items-end gap-6",
            ),
                class_name="flex min-h-screen w-full items-center justify-center p-6",
        ),
        password_reset_modal(),
        class_name=rx.cond(
            AuthState.dark_mode,
            "font-['Montserrat'] min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100",
            "font-['Montserrat'] min-h-screen bg-gradient-to-br from-cyan-50 via-white to-slate-100 text-slate-900",
        ),
    )


def password_reset_modal() -> rx.Component:
    return rx.cond(
        AuthState.show_password_reset_modal,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Reset Password",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-lg font-semibold text-white",
                        "text-lg font-semibold text-slate-900",
                    ),
                ),
                rx.el.p(
                    "Enter your account email. We'll generate a temporary password you can use immediately.",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-sm text-slate-300",
                        "text-sm text-slate-600",
                    ),
                ),
                rx.el.input(
                    placeholder="your.email@example.com",
                    value=AuthState.reset_email,
                    on_change=AuthState.set_reset_email,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "mt-4 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 placeholder:text-slate-400 focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                        "mt-4 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                    ),
                ),
                rx.cond(
                    AuthState.reset_error,
                    rx.el.p(
                        AuthState.reset_error,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "mt-2 text-sm text-red-300",
                            "mt-2 text-sm text-red-600",
                        ),
                    ),
                    None,
                ),
                rx.cond(
                    AuthState.issued_temp_password,
                    rx.el.div(
                        rx.el.span(
                            "Temporary password:",
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "text-xs font-semibold uppercase text-slate-300",
                                "text-xs font-semibold uppercase text-slate-600",
                            ),
                        ),
                        rx.el.code(
                            AuthState.issued_temp_password,
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "mx-auto mt-2 inline-flex items-center rounded-lg bg-white/10 px-3 py-1 text-sm font-semibold text-cyan-200",
                                "mx-auto mt-2 inline-flex items-center rounded-lg bg-cyan-50 px-3 py-1 text-sm font-semibold text-cyan-700",
                            ),
                        ),
                        rx.el.p(
                            "Use this password to sign in, then update it from your profile.",
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "mt-2 text-xs text-slate-300",
                                "mt-2 text-xs text-slate-600",
                            ),
                        ),
                        class_name="mt-4 flex flex-col items-center text-center",
                    ),
                    None,
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=AuthState.close_password_reset_modal,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20",
                            "inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-200",
                        ),
                    ),
                    rx.el.button(
                        "Generate Temporary Password",
                        on_click=AuthState.issue_temporary_password,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-2 focus:ring-cyan-300/40",
                            "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-2 focus:ring-teal-300/40",
                        ),
                    ),
                    class_name="mt-6 flex items-center justify-end gap-3",
                ),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "w-[90vw] max-w-md rounded-3xl border border-white/10 bg-slate-950/95 p-6 shadow-2xl backdrop-blur-2xl",
                    "w-[90vw] max-w-md rounded-3xl border border-white/60 bg-white p-6 shadow-2xl",
                ),
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4",
        ),
        None,
    )
