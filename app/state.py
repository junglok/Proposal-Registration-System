import reflex as rx
import re
import time
import bcrypt
from typing import Optional, TypedDict
import datetime
import uuid


class User:
    def __init__(self, email: str, password_hash: str, is_admin: bool = False):
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin


class Proposal(TypedDict):
    id: str
    user_email: str
    full_name: str
    email: str
    affiliation: str
    phone_number: str
    title: str
    description: str
    proposal_file: str
    created_at: str
    status: str
    review_results: str


class Database:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.proposals: dict[str, Proposal] = {}

    def get_user(self, email: str) -> Optional[User]:
        return self.users.get(email)

    def add_user(self, user: User):
        self.users[user.email] = user

    def add_proposal(self, proposal: Proposal):
        self.proposals[proposal["id"]] = proposal

    def get_user_proposals(self, email: str) -> list[Proposal]:
        return [p for p in self.proposals.values() if p["user_email"] == email]


db = Database()
admin_email = "admin@example.com"
if not db.get_user(admin_email):
    admin_password_hash = bcrypt.hashpw(
        "admin123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    admin_user = User(
        email=admin_email, password_hash=admin_password_hash, is_admin=True
    )
    db.add_user(admin_user)


class AuthState(rx.State):
    authenticated_user: Optional[str] = None
    active_page: str = "dashboard"
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    email_error: Optional[str] = None
    password_error: Optional[str] = None
    confirm_password_error: Optional[str] = None
    loading: bool = False

    def _validate_email(self):
        if not self.email:
            self.email_error = "Email is required."
        elif not re.match("[^@]+@[^@]+\\.[^@]+", self.email):
            self.email_error = "Invalid email address."
        else:
            self.email_error = None

    def _validate_password(self):
        if not self.password:
            self.password_error = "Password is required."
        elif len(self.password) < 8:
            self.password_error = "Password must be at least 8 characters."
        else:
            self.password_error = None

    def _validate_confirm_password(self):
        if not self.confirm_password:
            self.confirm_password_error = "Please confirm your password."
        elif self.password != self.confirm_password:
            self.confirm_password_error = "Passwords do not match."
        else:
            self.confirm_password_error = None

    @rx.event
    def on_email_change(self, value: str):
        self.email = value
        self._validate_email()

    @rx.event
    def on_password_change(self, value: str):
        self.password = value
        self._validate_password()
        if self.confirm_password:
            self._validate_confirm_password()

    @rx.event
    def on_confirm_password_change(self, value: str):
        self.confirm_password = value
        self._validate_confirm_password()

    def _validate_signup_fields(self):
        self._validate_email()
        self._validate_password()
        self._validate_confirm_password()

    def _validate_signin_fields(self):
        self._validate_email()
        self._validate_password()

    @rx.var
    def is_signin_form_valid(self) -> bool:
        return bool(
            self.email
            and self.password
            and (not self.email_error)
            and (not self.password_error)
        )

    @rx.var
    def is_signup_form_valid(self) -> bool:
        return self.is_signin_form_valid and bool(
            self.confirm_password and (not self.confirm_password_error)
        )

    @rx.event
    def handle_signin(self):
        self._validate_signin_fields()
        if not self.is_signin_form_valid:
            return rx.toast.error("Please correct the errors before submitting.")
        self.loading = True
        yield
        time.sleep(1)
        user = db.get_user(self.email)
        if user and bcrypt.checkpw(
            self.password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            self.authenticated_user = user.email
            self.loading = False
            yield rx.redirect("/dashboard")
            yield rx.toast.success("Signed in successfully!")
        else:
            self.loading = False
            yield rx.toast.error("Invalid email or password.")

    @rx.event
    def handle_signup(self):
        self._validate_signup_fields()
        if not self.is_signup_form_valid:
            return rx.toast.error("Please correct the errors before submitting.")
        self.loading = True
        yield
        time.sleep(1)
        if db.get_user(self.email):
            self.loading = False
            yield rx.toast.error("User with this email already exists.")
            return
        hashed_password = bcrypt.hashpw(
            self.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        new_user = User(email=self.email, password_hash=hashed_password)
        db.add_user(new_user)
        self.loading = False
        yield rx.toast.success("Account created successfully!")
        yield rx.redirect("/signin")

    @rx.event
    def set_active_page(self, page: str):
        self.active_page = page
        self._reset_fields()

    def _reset_fields(self):
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.email_error = None
        self.password_error = None
        self.confirm_password_error = None
        self.loading = False

    @rx.event
    def set_page(self, page: str):
        pass

    @rx.event
    def logout(self):
        self.authenticated_user = None
        self._reset_fields()
        return rx.redirect("/signin")

    @rx.var
    def is_authenticated(self) -> bool:
        return self.authenticated_user is not None

    @rx.var
    def is_admin(self) -> bool:
        if self.authenticated_user:
            user = db.get_user(self.authenticated_user)
            return user.is_admin if user else False
        return False

    @rx.event
    def check_auth(self):
        if not self.is_authenticated:
            return rx.redirect("/signin")