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
    return rx.el.div(
        rx.el.div(
            rx.icon(tag=icon_tag, class_name="h-5 w-5 text-gray-400"),
            class_name="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3",
        ),
        rx.el.input(
            placeholder=placeholder,
            type=field_type,
            default_value=value,
            on_change=on_change,
            class_name=rx.cond(
                error,
                "block w-full rounded-lg border border-red-300 bg-red-50 py-2.5 pl-10 pr-3 text-sm text-red-900 placeholder-red-400 transition-all duration-150 ease-in-out focus:border-red-500 focus:outline-none focus:ring-red-500",
                "block w-full rounded-lg border border-gray-200 bg-gray-50 py-2.5 pl-10 pr-3 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500",
            ),
        ),
        rx.cond(error, rx.el.p(error, class_name="mt-2 text-xs text-red-600"), None),
        class_name="relative",
    )


def _auth_button(
    text: str, is_valid: rx.Var[bool], on_click: rx.event.EventHandler
) -> rx.Component:
    return rx.el.button(
        rx.cond(AuthState.loading, rx.spinner(class_name="h-5 w-5 text-white"), text),
        on_click=on_click,
        disabled=~is_valid | AuthState.loading,
        class_name="flex w-full items-center justify-center rounded-lg bg-gradient-to-r from-teal-500 to-cyan-600 px-5 py-2.5 text-sm font-medium text-white shadow-md transition-all duration-150 ease-in-out hover:from-teal-600 hover:to-cyan-700 focus:outline-none focus:ring-4 focus:ring-teal-300 disabled:cursor-not-allowed disabled:opacity-50",
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
            rx.icon("file-text", class_name="h-8 w-8 text-teal-500"),
            rx.el.h1(
                "[GSDC TEM 활용지원 프로그램] 활용계획서 제출",
                class_name="text-xl font-bold tracking-tighter text-gray-800 text-center",
            ),
            class_name="mb-6 flex flex-col items-center justify-center gap-2",
        ),
        rx.el.div(
            rx.el.h2(title, class_name="text-xl font-semibold text-gray-900"),
            rx.el.div(*children, class_name="mt-6 space-y-4"),
            class_name="w-full",
        ),
        rx.el.p(
            toggle_text,
            " ",
            rx.el.a(
                toggle_link_text,
                href=toggle_link_href,
                class_name="font-medium text-teal-600 hover:underline",
            ),
            class_name="mt-6 text-center text-sm text-gray-600",
        ),
        class_name="flex w-full max-w-sm flex-col items-center rounded-xl border border-gray-200 bg-white p-8 shadow-lg",
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
            rx.el.a(
                "Forgot password?",
                href="#",
                class_name="text-sm font-medium text-teal-600 hover:underline",
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
            card, class_name="flex min-h-screen w-full items-center justify-center p-4"
        ),
        class_name="font-['Montserrat'] min-h-screen bg-gradient-to-br from-teal-50 to-cyan-100",
    )