import reflex as rx
import re
import bcrypt
from typing import Any, Optional, TypedDict
import datetime
import uuid
import sqlite3
import threading
from pathlib import Path
import secrets
import string


class User:
    def __init__(self, email: str, password_hash: str, is_admin: bool = False, must_reset_password: bool = False):
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.must_reset_password = must_reset_password


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
    updated_at: str
    status: str
    review_results: str


class Database:
    def __init__(self, db_path: Optional[str | Path] = None):
        default_path = Path(__file__).resolve().parent.parent / "proposal_app.db"
        self.db_path = Path(db_path) if db_path else default_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._initialize()

    def _initialize(self):
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    is_admin INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    must_reset_password INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    affiliation TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    proposal_file TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    review_results TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
                """
            )
            # Ensure schema includes updated_at and must_reset_password for existing databases.
            cursor = self._conn.execute("PRAGMA table_info(proposals)")
            proposal_columns = {row["name"] for row in cursor.fetchall()}
            if "updated_at" not in proposal_columns:
                self._conn.execute(
                    "ALTER TABLE proposals ADD COLUMN updated_at TEXT DEFAULT ''"
                )
                self._conn.execute(
                    """
                    UPDATE proposals
                    SET updated_at = CASE
                        WHEN updated_at IS NULL OR updated_at = '' THEN created_at
                        ELSE updated_at
                    END
                    """
                )
            cursor = self._conn.execute("PRAGMA table_info(users)")
            user_columns = {row["name"] for row in cursor.fetchall()}
            if "must_reset_password" not in user_columns:
                self._conn.execute(
                    "ALTER TABLE users ADD COLUMN must_reset_password INTEGER NOT NULL DEFAULT 0"
                )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_proposals_user_email ON proposals(user_email)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status)"
            )
            self._conn.commit()

    def _row_to_proposal(self, row: sqlite3.Row) -> Proposal:
        return Proposal(
            id=row["id"],
            user_email=row["user_email"],
            full_name=row["full_name"],
            email=row["email"],
            affiliation=row["affiliation"],
            phone_number=row["phone_number"],
            title=row["title"],
            description=row["description"],
            proposal_file=row["proposal_file"],
            created_at=row["created_at"],
            updated_at=row["updated_at"] or row["created_at"],
            status=row["status"],
            review_results=row["review_results"] or "",
        )

    def get_user(self, email: str) -> Optional[User]:
        with self._lock:
            cursor = self._conn.execute(
                "SELECT email, password_hash, is_admin, must_reset_password FROM users WHERE email = ?",
                (email,),
            )
            row = cursor.fetchone()
        if row:
            return User(
                email=row["email"],
                password_hash=row["password_hash"],
                is_admin=bool(row["is_admin"]),
                must_reset_password=bool(row["must_reset_password"]),
            )
        return None

    def add_user(self, user: User):
        try:
            with self._lock:
                self._conn.execute(
                    """
                    INSERT INTO users (email, password_hash, is_admin, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user.email,
                        user.password_hash,
                        1 if user.is_admin else 0,
                        datetime.datetime.now().isoformat(),
                    ),
                )
                self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("User already exists.") from exc

    def add_proposal(self, proposal: Proposal):
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO proposals (
                    id,
                    user_email,
                    full_name,
                    email,
                    affiliation,
                    phone_number,
                    title,
                    description,
                    proposal_file,
                    created_at,
                    updated_at,
                    status,
                    review_results
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal["id"],
                    proposal["user_email"],
                    proposal["full_name"],
                    proposal["email"],
                    proposal["affiliation"],
                    proposal["phone_number"],
                    proposal["title"],
                    proposal["description"],
                    proposal["proposal_file"],
                    proposal["created_at"],
                    proposal["updated_at"],
                    proposal["status"],
                    proposal["review_results"],
                ),
            )
            self._conn.commit()

    def get_user_proposals(self, email: str) -> list[Proposal]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT *
                FROM proposals
                WHERE user_email = ?
                ORDER BY datetime(created_at) DESC
                """,
                (email,),
            )
            rows = cursor.fetchall()
        return [self._row_to_proposal(row) for row in rows]

    def get_all_proposals(self) -> list[Proposal]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT *
                FROM proposals
                ORDER BY datetime(created_at) DESC
                """
            )
            rows = cursor.fetchall()
        return [self._row_to_proposal(row) for row in rows]

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM proposals WHERE id = ?", (proposal_id,)
            )
            row = cursor.fetchone()
        if row:
            return self._row_to_proposal(row)
        return None

    def update_proposal(self, proposal_id: str, updates: dict[str, str]) -> bool:
        if not updates:
            return False
        updates = dict(updates)
        updates["updated_at"] = datetime.datetime.now().isoformat()
        columns = ", ".join(f"{key} = ?" for key in updates)
        values = list(updates.values())
        values.append(proposal_id)
        with self._lock:
            cursor = self._conn.execute(
                f"UPDATE proposals SET {columns} WHERE id = ?", values
            )
            self._conn.commit()
            if cursor.rowcount > 0:
                return True
            exists_cursor = self._conn.execute(
                "SELECT 1 FROM proposals WHERE id = ?", (proposal_id,)
            )
            return exists_cursor.fetchone() is not None

    def update_proposal_status(
        self, proposal_id: str, status: str, review_results: str
    ) -> bool:
        return self.update_proposal(
            proposal_id,
            {
                "status": status,
                "review_results": review_results,
            },
        )


    def update_user_password(
        self, email: str, password_hash: str, must_reset: bool = False
    ) -> bool:
        with self._lock:
            cursor = self._conn.execute(
                "UPDATE users SET password_hash = ?, must_reset_password = ? WHERE email = ?",
                (password_hash, 1 if must_reset else 0, email),
            )
            self._conn.commit()
            return cursor.rowcount > 0
    def delete_proposal(self, proposal_id: str) -> bool:
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM proposals WHERE id = ?", (proposal_id,)
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def list_users(self) -> list[dict[str, str]]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT email, created_at, is_admin
                FROM users
                ORDER BY datetime(created_at) DESC
                """
            )
            return [
                {
                    "email": row["email"],
                    "created_at": row["created_at"],
                    "created_label": (row["created_at"] or "").replace("T", " ")[:19] if row["created_at"] else "N/A",
                    "is_admin": bool(row["is_admin"]),
                }
                for row in cursor.fetchall()
            ]


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
    dark_mode: bool = False
    reset_email: str = ""
    reset_error: Optional[str] = None
    issued_temp_password: str = ""
    show_password_reset_modal: bool = False
    show_force_password_modal: bool = False
    new_password: str = ""
    new_password_confirm: str = ""
    new_password_error: Optional[str] = None

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
        user = db.get_user(self.email)
        if user and bcrypt.checkpw(
            self.password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            self.authenticated_user = user.email
            self.loading = False
            self.show_force_password_modal = bool(getattr(user, 'must_reset_password', False))
            if self.show_force_password_modal:
                self.new_password = ""
                self.new_password_confirm = ""
                self.new_password_error = None
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
        if db.get_user(self.email):
            self.loading = False
            yield rx.toast.error("User with this email already exists.")
            return
        hashed_password = bcrypt.hashpw(
            self.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        new_user = User(email=self.email, password_hash=hashed_password)
        try:
            db.add_user(new_user)
        except ValueError:
            self.loading = False
            yield rx.toast.error("User with this email already exists.")
            return
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
        self.reset_email = ""
        self.reset_error = None
        self.issued_temp_password = ""
        self.show_password_reset_modal = False

    @rx.event
    def set_page(self, page: str):
        pass

    @rx.event
    def logout(self):
        self.authenticated_user = None
        self._reset_fields()
        self.show_force_password_modal = False
        self.new_password = ""
        self.new_password_confirm = ""
        self.new_password_error = None
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

    @rx.event
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    @rx.var
    def app_shell_classes(self) -> str:
        return (
            "bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-slate-100"
            if self.dark_mode
            else "bg-gradient-to-br from-slate-100 via-white to-slate-50 text-slate-900"
        )

    @rx.var
    def sidebar_classes(self) -> str:
        return (
            "hidden md:flex md:flex-col min-h-screen w-64 shrink-0 border-r border-white/10 bg-slate-900/60 text-slate-100 backdrop-blur-xl"
            if self.dark_mode
            else "hidden md:flex md:flex-col min-h-screen w-64 shrink-0 border-r border-white/40 bg-white/70 text-slate-900 backdrop-blur-xl"
        )

    @rx.var
    def surface_card(self) -> str:
        return (
            "bg-white/80 border border-white/30 shadow-xl backdrop-blur-xl"
            if not self.dark_mode
            else "bg-white/10 border border-white/10 shadow-2xl backdrop-blur-2xl"
        )

    @rx.var
    def muted_text_class(self) -> str:
        return "text-slate-400" if self.dark_mode else "text-slate-500"

    @rx.var
    def accent_button(self) -> str:
        return (
            "bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-500 hover:to-emerald-500 text-white"
            if not self.dark_mode
            else "bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-indigo-400 text-slate-900"
        )

    @rx.event
    def open_password_reset_modal(self):
        self.reset_email = (self.email or "").strip()
        self.reset_error = None
        self.issued_temp_password = ""
        self.show_password_reset_modal = True

    @rx.event
    def close_password_reset_modal(self):
        self.show_password_reset_modal = False

    @rx.event
    def set_reset_email(self, value: str):
        self.reset_email = value
        self.reset_error = None
        self.issued_temp_password = ""

    def _validate_reset_email(self):
        if not self.reset_email.strip():
            self.reset_error = "Email is required."
        elif not re.match("[^@]+@[^@]+\\.[^@]+", self.reset_email.strip()):
            self.reset_error = "Invalid email address."
        else:
            self.reset_error = None

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value
        self.new_password_error = None

    @rx.event
    def set_new_password_confirm(self, value: str):
        self.new_password_confirm = value
        self.new_password_error = None

    @rx.event
    def submit_new_password(self):
        if not self.authenticated_user:
            return rx.toast.error("You must be signed in.")
        if not self._validate_new_passwords():
            return
        hashed = bcrypt.hashpw(
            self.new_password.strip().encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        if not db.update_user_password(self.authenticated_user, hashed, must_reset=False):
            return rx.toast.error("Unable to update password. Please try again.")
        self.new_password = ""
        self.new_password_confirm = ""
        self.new_password_error = None
        self.show_force_password_modal = False
        return rx.toast.success("Password updated successfully.")

    def _validate_new_passwords(self):
        new = self.new_password.strip()
        confirm = self.new_password_confirm.strip()
        if not new:
            self.new_password_error = "Password is required."
            return False
        if len(new) < 8:
            self.new_password_error = "Password must be at least 8 characters."
            return False
        if new != confirm:
            self.new_password_error = "Passwords do not match."
            return False
        self.new_password = new
        self.new_password_confirm = confirm
        self.new_password_error = None
        return True

    @rx.event
    def issue_temporary_password(self):
        self._validate_reset_email()
        if self.reset_error:
            return
        lookup_email = self.reset_email.strip()
        self.reset_email = lookup_email
        user = db.get_user(lookup_email)
        if not user:
            self.reset_error = "No account found with this email."
            return
        temp_password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
        )
        password_hash = bcrypt.hashpw(
            temp_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        if not db.update_user_password(user.email, password_hash, must_reset=True):
            return rx.toast.error("Failed to update password.")
        self.show_password_reset_modal = True
        self.show_force_password_modal = False
        self.new_password = ""
        self.new_password_confirm = ""
        self.new_password_error = None
        self.issued_temp_password = temp_password
        self.reset_error = None
        return rx.toast.success("Temporary password generated.")
