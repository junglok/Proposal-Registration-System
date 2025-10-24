import reflex as rx
from app.state import AuthState, Proposal
from app.states.proposal_state import ProposalState
from app.states.admin_state import AdminState


def _metric_card(
    title: str, value: rx.Var, icon: str, gradient: str, subtext: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(tag=icon, class_name="h-5 w-5 text-white"),
                class_name=f"inline-flex items-center justify-center rounded-full bg-gradient-to-br {gradient} p-2 shadow-lg",
            ),
            rx.el.span(title, class_name="text-sm font-semibold tracking-wide"),
            class_name="flex items-center justify-between gap-4",
        ),
        rx.el.div(
            rx.el.span(
                value,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-3xl font-semibold text-white",
                    "text-3xl font-semibold text-slate-900",
                ),
            ),
            rx.el.span(
                subtext,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-xs font-medium text-white/70",
                    "text-xs font-medium text-slate-500",
                ),
            ),
            class_name="mt-4 flex flex-col",
        ),
        class_name=rx.cond(
            AuthState.dark_mode,
            "relative overflow-hidden rounded-2xl border border-white/10 bg-white/10 p-5 shadow-xl backdrop-blur-xl",
            "relative overflow-hidden rounded-2xl border border-white/60 bg-white p-5 shadow-xl backdrop-blur-sm",
        ),
    )


def dashboard_topbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                rx.match(
                    AuthState.active_page,
                    ("dashboard", "Welcome back"),
                    ("create_proposal", "Craft a new proposal"),
                    ("my_proposals", "Your proposals"),
                    ("admin_panel", "Administrator Overview"),
                    ("user_panel", "User directory"),
                    "Dashboard",
                ),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-3xl font-semibold tracking-tight text-white",
                    "text-3xl font-semibold tracking-tight text-slate-900",
                ),
            ),
            rx.el.p(
                "Manage submissions, track reviews, and collaborate effortlessly.",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-sm mt-2 max-w-2xl text-slate-300",
                    "text-sm mt-2 max-w-2xl text-slate-600",
                ),
            ),
            class_name="flex flex-col",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon(
                    tag=rx.cond(
                        AuthState.dark_mode,
                        "sun",
                        "moon",
                    ),
                    class_name="h-4 w-4",
                ),
                rx.cond(AuthState.dark_mode, "Light Mode", "Dark Mode"),
                on_click=AuthState.toggle_dark_mode,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow-lg backdrop-blur transition hover:bg-white/20",
                    "inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700 shadow-md transition hover:bg-slate-100",
                ),
            ),
            class_name="flex items-center gap-3",
        ),
        class_name="flex flex-col gap-4 md:flex-row md:items-center md:justify-between",
    )


def force_password_change_modal() -> rx.Component:
    return rx.cond(
        AuthState.show_force_password_modal,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Update Password",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-lg font-semibold text-white",
                        "text-lg font-semibold text-slate-900",
                    ),
                ),
                rx.el.p(
                    "A temporary password was issued for your account. Please choose a new password to continue.",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-sm text-slate-300",
                        "text-sm text-slate-600",
                    ),
                ),
                rx.el.input(
                    placeholder="New password",
                    type="password",
                    value=AuthState.new_password,
                    on_change=AuthState.set_new_password,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "mt-4 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 placeholder:text-slate-400 focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                        "mt-4 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                    ),
                ),
                rx.el.input(
                    placeholder="Confirm password",
                    type="password",
                    value=AuthState.new_password_confirm,
                    on_change=AuthState.set_new_password_confirm,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "mt-3 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 placeholder:text-slate-400 focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                        "mt-3 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                    ),
                ),
                rx.cond(
                    AuthState.new_password_error,
                    rx.el.p(
                        AuthState.new_password_error,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "mt-2 text-sm text-red-300",
                            "mt-2 text-sm text-red-600",
                        ),
                    ),
                    None,
                ),
                rx.el.div(
                    rx.el.button(
                        "Update Password",
                        on_click=AuthState.submit_new_password,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-2 focus:ring-cyan-300/40",
                            "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-2 focus:ring-teal-300/40",
                        ),
                    ),
                    rx.el.button(
                        "Sign out",
                        on_click=AuthState.logout,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-slate-100 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20",
                            "inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-200",
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


def dashboard_home() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Welcome back, {AuthState.authenticated_user}",
                class_name="text-2xl font-semibold tracking-tight",
            ),
            rx.el.p(
                "Here is a quick snapshot of your proposal activity.",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-sm text-slate-300",
                    "text-sm text-slate-500",
                ),
            ),
            class_name="flex flex-col gap-2",
        ),
        rx.el.div(
            _metric_card(
                "Total Proposals",
                ProposalState.total_proposals_count,
                "folder",
                "from-cyan-500 via-blue-500 to-indigo-500",
                "All submissions you have created.",
            ),
            _metric_card(
                "Under Review",
                ProposalState.under_review_count,
                "shield-check",
                "from-purple-500 via-indigo-500 to-blue-500",
                "Awaiting the admin decision.",
            ),
            _metric_card(
                "Approved",
                ProposalState.approved_count,
                "circle-check",
                "from-emerald-500 via-teal-500 to-cyan-500",
                "Successfully approved proposals.",
            ),
            class_name="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Latest Updates",
                    class_name="text-lg font-semibold tracking-tight",
                ),
                rx.el.p(
                    "Keep an eye on new review results or comments from the team.",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-sm text-slate-300",
                        "text-sm text-slate-500",
                    ),
                ),
                class_name="flex flex-col gap-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(tag="sparkles", class_name="h-4 w-4 text-cyan-400"),
                    "No new notifications — you're all caught up!",
                    class_name="flex items-center gap-2 text-sm",
                ),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl",
                    "rounded-2xl border border-white/60 bg-white p-6 backdrop-blur",
                ),
            ),
            class_name="mt-8 space-y-6",
        ),
        class_name="space-y-8",
    )


def _form_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    error: rx.Var[str],
    type: str = "text",
) -> rx.Component:
    label_class = rx.cond(
        AuthState.dark_mode,
        "block text-sm font-medium text-slate-200 mb-2",
        "block text-sm font-medium text-slate-700 mb-2",
    )
    input_base = rx.cond(
        AuthState.dark_mode,
        "block w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 placeholder:text-slate-400 transition-all duration-150 ease-in-out focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
        "block w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 transition-all duration-150 ease-in-out focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
    )
    input_error = rx.cond(
        AuthState.dark_mode,
        "block w-full rounded-xl border border-red-400 bg-red-900/40 p-3 text-sm text-red-100 placeholder:text-red-200 transition-all duration-150 ease-in-out focus:border-red-400 focus:outline-none focus:ring-2 focus:ring-red-400/30",
        "block w-full rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-900 placeholder:text-red-400 transition-all duration-150 ease-in-out focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30",
    )
    error_text = rx.cond(
        AuthState.dark_mode,
        "mt-1 text-xs text-red-300",
        "mt-1 text-xs text-red-600",
    )
    return rx.el.div(
        rx.el.label(label, class_name=label_class),
        rx.el.input(
            placeholder=placeholder,
            default_value=value,
            on_change=on_change,
            type=type,
            class_name=rx.cond(error, input_error, input_base),
        ),
        rx.cond(error, rx.el.p(error, class_name=error_text), None),
    )


def create_proposal_form() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            rx.cond(ProposalState.is_editing, "Edit Proposal", "Create New Proposal"),
            class_name=rx.cond(
                AuthState.dark_mode,
                "text-3xl font-semibold tracking-tight text-white",
                "text-3xl font-semibold tracking-tight text-slate-900",
            ),
        ),
        rx.el.form(
            rx.el.div(
                _form_field(
                    "Full Name",
                    "John Doe",
                    ProposalState.full_name,
                    ProposalState.set_full_name,
                    ProposalState.full_name_error,
                ),
                _form_field(
                    "Email",
                    "john.doe@example.com",
                    ProposalState.proposal_email,
                    ProposalState.set_proposal_email,
                    ProposalState.proposal_email_error,
                    type="email",
                ),
                _form_field(
                    "Affiliation",
                    "University of Reflex",
                    ProposalState.affiliation,
                    ProposalState.set_affiliation,
                    ProposalState.affiliation_error,
                ),
                _form_field(
                    "Phone Number",
                    "(123) 456-7890",
                    ProposalState.phone_number,
                    ProposalState.set_phone_number,
                    ProposalState.phone_number_error,
                    type="tel",
                ),
                _form_field(
                    "Proposal Title",
                    "A new study on...",
                    ProposalState.title,
                    ProposalState.set_title,
                    ProposalState.title_error,
                ),
                rx.el.div(
                    rx.el.label(
                        "Description",
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "block text-sm font-medium text-slate-200 mb-2",
                            "block text-sm font-medium text-slate-700 mb-2",
                        ),
                    ),
                    rx.el.textarea(
                        placeholder="Detailed description of your proposal...",
                        default_value=ProposalState.description,
                        on_change=ProposalState.set_description,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "block w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 placeholder:text-slate-400 transition-all duration-150 ease-in-out focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30 min-h-[140px]",
                            "block w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 transition-all duration-150 ease-in-out focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 min-h-[140px]",
                        ),
                    ),
                    rx.cond(
                        ProposalState.description_error,
                        rx.el.p(
                            ProposalState.description_error,
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "mt-1 text-xs text-red-300",
                                "mt-1 text-xs text-red-600",
                            ),
                        ),
                        None,
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Proposal Document",
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "block text-sm font-medium text-slate-200 mb-2",
                            "block text-sm font-medium text-slate-700 mb-2",
                        ),
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                tag="cloud_upload",
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "h-8 w-8 text-cyan-300",
                                    "h-8 w-8 text-cyan-500",
                                ),
                            ),
                            rx.el.p("Drag & drop or click to upload"),
                            rx.el.span(
                                "PDF, DOC, DOCX, HWP up to 50MB",
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-xs text-slate-300",
                                    "text-xs text-slate-500",
                                ),
                            ),
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "flex flex-col items-center justify-center gap-1 rounded-2xl border-2 border-dashed border-white/20 bg-white/5 p-6 text-slate-100 transition hover:bg-white/10",
                                "flex flex-col items-center justify-center gap-1 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-6 text-slate-700 transition hover:bg-slate-100",
                            ),
                        ),
                        id="proposal_upload",
                        accept={
                            "application/pdf": [".pdf"],
                            "application/msword": [".doc"],
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                                ".docx"
                            ],
                            "application/x-hwp": [".hwp"],
                        },
                        max_files=1,
                        max_size=50 * 1024 * 1024,
                        class_name="w-full",
                    ),
                    rx.el.div(
                        rx.foreach(
                            rx.selected_files("proposal_upload"),
                            lambda file_name: rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "file-text",
                                        class_name=rx.cond(
                                            AuthState.dark_mode,
                                            "h-4 w-4 text-cyan-300",
                                            "h-4 w-4 text-cyan-600",
                                        ),
                                    ),
                                    rx.el.span(
                                        file_name,
                                        class_name=rx.cond(
                                            AuthState.dark_mode,
                                            "flex-1 text-sm text-slate-100 truncate",
                                            "flex-1 text-sm text-slate-700 truncate",
                                        ),
                                    ),
                                    class_name="flex items-center gap-2",
                                ),
                                rx.el.button(
                                    rx.icon(tag="trash-2", class_name="mr-1 h-4 w-4"),
                                    "Remove",
                                    on_click=ProposalState.remove_selected_upload,
                                    class_name="inline-flex items-center rounded-md bg-red-500 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition duration-150 hover:bg-red-600 focus:outline-none focus:ring-4 focus:ring-red-200/60",
                                ),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/5 p-3 text-sm backdrop-blur",
                                    "flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm",
                                ),
                            ),
                        )
                    ),
                    rx.cond(
                        ProposalState.proposal_file_error,
                        rx.el.p(
                            ProposalState.proposal_file_error,
                            class_name=rx.cond(
                                AuthState.dark_mode,
                                "mt-1 text-xs text-red-300",
                                "mt-1 text-xs text-red-600",
                            ),
                        ),
                        None,
                    ),
                ),
                class_name="space-y-6",
            ),
            rx.el.div(
                rx.el.button(
                    rx.cond(
                        ProposalState.loading,
                        rx.spinner(class_name="h-5 w-5"),
                        rx.cond(
                            ProposalState.is_editing,
                            "Update Proposal",
                            "Submit Proposal",
                        ),
                    ),
                    type="button",
                    on_click=rx.cond(
                        ProposalState.is_editing,
                        ProposalState.handle_update_proposal(
                            rx.upload_files(upload_id="proposal_upload")
                        ),
                        ProposalState.handle_create_proposal(
                            rx.upload_files(upload_id="proposal_upload")
                        ),
                    ),
                    disabled=ProposalState.loading,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "flex-1 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-5 py-3 text-sm font-semibold text-slate-900 shadow-xl transition duration-150 hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40 disabled:cursor-not-allowed disabled:opacity-60",
                        "flex-1 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-5 py-3 text-sm font-semibold text-white shadow-xl transition duration-150 hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40 disabled:cursor-not-allowed disabled:opacity-60",
                    ),
                ),
                rx.cond(
                    ProposalState.is_editing,
                    rx.el.button(
                        "Cancel",
                        type="button",
                        on_click=ProposalState.cancel_edit,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "flex-1 inline-flex items-center justify-center rounded-full border border-white/20 bg-white/10 px-5 py-3 text-sm font-semibold text-slate-100 shadow-md transition duration-150 hover:bg-white/20 focus:outline-none focus:ring-4 focus:ring-white/10",
                            "flex-1 inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-md transition duration-150 hover:bg-slate-100 focus:outline-none focus:ring-4 focus:ring-slate-200",
                        ),
                    ),
                    None,
                ),
                class_name="mt-8 flex gap-4 w-full",
            ),
            class_name=rx.cond(
                AuthState.dark_mode,
                "mt-8 max-w-2xl mx-auto rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-2xl",
                "mt-8 max-w-2xl mx-auto rounded-3xl border border-white/60 bg-white p-8 shadow-xl backdrop-blur",
            ),
        ),
    )


def _status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        status,
        class_name=rx.match(
            status,
            (
                "Submitted",
                "bg-blue-100 text-blue-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full w-fit",
            ),
            (
                "Under Review",
                "bg-yellow-100 text-yellow-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full w-fit",
            ),
            (
                "Approved",
                "bg-green-100 text-green-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full w-fit",
            ),
            (
                "Rejected",
                "bg-red-100 text-red-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full w-fit",
            ),
            "bg-gray-100 text-gray-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full w-fit",
        ),
    )


def _proposal_card(proposal: Proposal) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    proposal["title"],
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-lg font-semibold text-white",
                        "text-lg font-semibold text-slate-900",
                    ),
                ),
                _status_badge(proposal["status"]),
                class_name="flex items-center justify-between",
            ),
            rx.el.p(
                f"Affiliation: {proposal['affiliation']}",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-sm text-slate-300 mt-1",
                    "text-sm text-slate-600 mt-1",
                ),
            ),
            rx.el.p(
                f"Submitted: {proposal['created_at'].to_string().replace('T', ' ').split('.')[0]}",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-xs text-slate-400 mt-1",
                    "text-xs text-slate-500 mt-1",
                ),
            ),
            rx.el.p(
                f"Updated: {proposal['updated_at'].replace('T', ' ')[:19]}",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-xs text-slate-500",
                    "text-xs text-slate-500",
                ),
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.button(
                "View Details",
                on_click=lambda _: ProposalState.view_proposal_details(proposal),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "px-4 py-2 text-sm font-semibold text-slate-900 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 shadow-lg transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                    "px-4 py-2 text-sm font-semibold text-white rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 shadow-lg transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                ),
            ),
            rx.cond(
                proposal["status"] == "Submitted",
                rx.el.button(
                    "Delete",
                    on_click=lambda _: ProposalState.prompt_delete_proposal(
                        proposal["id"]
                    ),
                    class_name="px-4 py-2 text-sm font-semibold text-white rounded-full bg-red-500 shadow hover:bg-red-600 focus:outline-none focus:ring-4 focus:ring-red-200/60",
                ),
                None,
            ),
            class_name="flex items-center gap-2 mt-4 sm:mt-0 sm:ml-4",
        ),
        class_name=rx.cond(
            AuthState.dark_mode,
            "flex flex-col items-start justify-between gap-4 rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur sm:flex-row sm:items-center",
            "flex flex-col items-start justify-between gap-4 rounded-3xl border border-white/60 bg-white p-6 shadow-xl sm:flex-row sm:items-center",
        ),
    )


def my_proposals_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "My Proposals",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "text-3xl font-semibold tracking-tight text-white mb-6",
                    "text-3xl font-semibold tracking-tight text-slate-900 mb-6",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        tag="search",
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "h-5 w-5 text-slate-400",
                            "h-5 w-5 text-slate-400",
                        ),
                    ),
                    class_name="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3",
                ),
                rx.el.input(
                    placeholder="Search by title or description...",
                    on_change=ProposalState.set_search_query.debounce(300),
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "block w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-3 text-sm text-slate-100 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                        "block w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-800 transition focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                    ),
                ),
                class_name="relative flex-grow",
            ),
            rx.el.select(
                rx.el.option("All Statuses", value="All"),
                rx.el.option("Submitted", value="Submitted"),
                rx.el.option("Under Review", value="Under Review"),
                rx.el.option("Approved", value="Approved"),
                rx.el.option("Rejected", value="Rejected"),
                on_change=ProposalState.set_status_filter,
                default_value="All",
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "rounded-xl border border-white/10 bg-white/5 py-2.5 pl-3 pr-8 text-sm text-slate-100 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                    "rounded-xl border border-slate-200 bg-white py-2.5 pl-3 pr-8 text-sm text-slate-800 transition focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                ),
            ),
            rx.el.button(
                rx.icon(tag="refresh_cw", class_name="mr-2 h-4 w-4"),
                "Refresh",
                on_click=ProposalState.refresh_proposals,
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                    "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                ),
            ),
            class_name="flex flex-col sm:flex-row items-center gap-4 mb-6",
        ),
        rx.el.div(
            rx.foreach(ProposalState.filtered_proposals, _proposal_card),
            class_name="space-y-4",
        ),
        proposal_detail_modal(),
        delete_confirmation_dialog(),
    )


def proposal_detail_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(rx.el.div()),
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(class_name="fixed inset-0 bg-black/50"),
            rx.radix.primitives.dialog.content(
                rx.cond(
                    ProposalState.selected_proposal,
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                ProposalState.selected_proposal["title"],
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-xl font-bold text-white",
                                    "text-xl font-bold text-slate-900",
                                ),
                            ),
                            _status_badge(ProposalState.selected_proposal["status"]),
                            class_name="flex items-start justify-between",
                        ),
                        rx.el.div(
                            rx.el.div(
                                    rx.el.h3("Applicant", class_name="font-semibold"),
                                rx.el.p(ProposalState.selected_proposal["full_name"]),
                                rx.el.p(ProposalState.selected_proposal["email"]),
                                rx.el.p(
                                    ProposalState.selected_proposal["phone_number"]
                                ),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-sm text-slate-200",
                                    "text-sm text-slate-700",
                                ),
                            ),
                            rx.el.div(
                                rx.el.h3("Affiliation", class_name="font-semibold"),
                                rx.el.p(ProposalState.selected_proposal["affiliation"]),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-sm text-slate-200",
                                    "text-sm text-slate-700",
                                ),
                            ),
                            rx.el.div(
                                rx.el.h3("Submitted On", class_name="font-semibold"),
                                rx.el.p(
                                    ProposalState.selected_proposal["created_at"]
                                    .to_string()
                                    .replace("T", " ")
                                    .split(".")[0][1:]
                                ),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-sm text-slate-200",
                                    "text-sm text-slate-700",
                                ),
                            ),
                            rx.el.div(
                                rx.el.h3("Last Updated", class_name="font-semibold"),
                                rx.el.p(
                                    ProposalState.selected_proposal["updated_at"]
                                    .to_string()
                                    .replace("T", " ")
                                    .split(".")[0][1:]
                                ),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-sm text-slate-200",
                                    "text-sm text-slate-700",
                                ),
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Description", class_name="font-semibold mt-4 mb-2"
                            ),
                            rx.el.p(
                                ProposalState.selected_proposal["description"],
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "text-sm text-slate-200 bg-white/5 p-3 rounded-xl border border-white/10",
                                    "text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200",
                                ),
                            ),
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Uploaded Files", class_name="font-semibold mt-4 mb-2"
                            ),
                            rx.cond(
                                ProposalState.has_selected_proposal_files,
                                rx.el.ul(
                                    rx.foreach(
                                        ProposalState.selected_proposal_files,
                                        lambda file_name: rx.el.li(
                                            rx.el.div(
                                                rx.icon(
                                                    tag="file-text",
                                                    class_name=rx.cond(
                                                        AuthState.dark_mode,
                                                        "h-4 w-4 text-cyan-300",
                                                        "h-4 w-4 text-cyan-600",
                                                    ),
                                                ),
                                                rx.el.span(
                                                    file_name,
                                                    class_name=rx.cond(
                                                        AuthState.dark_mode,
                                                        "flex-1 text-sm text-slate-200 truncate",
                                                        "flex-1 text-sm text-slate-700 truncate",
                                                    ),
                                                ),
                                                class_name="flex items-center gap-2",
                                            ),
                                            rx.el.button(
                                                rx.icon(
                                                    tag="download",
                                                    class_name="mr-2 h-4 w-4",
                                                ),
                                                "Download",
                                                on_click=lambda _: ProposalState.download_proposal_file(
                                                    filename=file_name
                                                ),
                                                class_name=rx.cond(
                                                    AuthState.dark_mode,
                                                    "inline-flex items-center rounded-md bg-gradient-to-r from-cyan-400 to-blue-500 px-3 py-1.5 text-xs font-medium text-slate-900 shadow-sm transition duration-150 hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                                                    "inline-flex items-center rounded-md bg-gradient-to-r from-teal-500 to-cyan-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition duration-150 hover:from-teal-600 hover:to-cyan-700 focus:outline-none focus:ring-4 focus:ring-teal-300",
                                                ),
                                            ),
                                            class_name=rx.cond(
                                                AuthState.dark_mode,
                                                "flex items-center justify-between gap-4 rounded-lg border border-white/10 bg-white/5 p-3 shadow-sm backdrop-blur",
                                                "flex items-center justify-between gap-4 rounded-lg border border-slate-200 bg-white p-3 shadow-sm",
                                            ),
                                        ),
                                    ),
                                    class_name="space-y-2",
                                ),
                                rx.el.p(
                                    "No files uploaded.",
                                    class_name=rx.cond(
                                        AuthState.dark_mode,
                                        "text-sm text-slate-400",
                                        "text-sm text-slate-500",
                                    ),
                                ),
                            ),
                        ),
                        rx.cond(
                            ProposalState.selected_proposal["review_results"],
                            rx.el.div(
                                rx.el.h3(
                                    "Review Results",
                                    class_name="font-semibold mt-4 mb-2",
                                ),
                                rx.el.p(
                                    ProposalState.selected_proposal["review_results"],
                                    class_name=rx.cond(
                                        AuthState.dark_mode,
                                        "text-sm text-slate-200 bg-cyan-500/10 p-3 rounded-xl border border-cyan-400/40",
                                        "text-sm text-slate-700 bg-blue-50 p-3 rounded-xl border border-blue-200",
                                    ),
                                ),
                            ),
                            None,
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon(tag="download", class_name="mr-2 h-4 w-4"),
                                "Download Document",
                                on_click=ProposalState.download_proposal_file,
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                                    "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                                ),
                            ),
                            rx.cond(
                ProposalState.selected_proposal["user_email"]
                == AuthState.authenticated_user,
                rx.el.button(
                    rx.icon(tag="copy", class_name="mr-2 h-4 w-4"),
                    "Edit Proposal",
                    on_click=ProposalState.load_proposal_for_edit,
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-slate-100 shadow hover:bg-white/20 focus:outline-none focus:ring-4 focus:ring-white/20",
                        "inline-flex items-center rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300/60",
                    ),
                ),
                None,
            ),
            class_name="flex items-center gap-4 mt-6",
        ),
                        rx.cond(
                            AdminState.is_admin,
                            rx.el.div(
                                rx.el.h3(
                                    "Admin Actions",
                                    class_name="font-semibold mt-6 mb-2",
                                ),
                                rx.el.div(
                                    rx.el.select(
                                        rx.el.option("Submitted", value="Submitted"),
                                        rx.el.option(
                                            "Under Review", value="Under Review"
                                        ),
                                        rx.el.option("Approved", value="Approved"),
                                        rx.el.option("Rejected", value="Rejected"),
                                        default_value=ProposalState.selected_proposal[
                                            "status"
                                        ],
                                        on_change=lambda status: AdminState.update_proposal_status(
                                            ProposalState.selected_proposal["id"],
                                            status,
                                        ),
                                        class_name=rx.cond(
                                            AuthState.dark_mode,
                                            "rounded-xl border border-white/10 bg-white/5 text-sm text-slate-100 focus:border-cyan-400/80 focus:ring-cyan-400/40 w-full sm:w-auto mb-2",
                                            "rounded-xl border border-slate-200 bg-white text-sm text-slate-800 focus:border-teal-500 focus:ring-teal-500/40 w-full sm:w-auto mb-2",
                                        ),
                                    ),
                                    rx.el.textarea(
                                        placeholder="Add review results...",
                                        default_value=AdminState.review_results_input,
                                        on_change=AdminState.set_review_results_input,
                                        class_name=rx.cond(
                                            AuthState.dark_mode,
                                            "block w-full rounded-xl border border-white/10 bg-white/5 p-2 text-sm text-slate-100 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/40 min-h-[80px]",
                                            "block w-full rounded-xl border border-slate-200 bg-white p-2 text-sm text-slate-800 transition focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/30 min-h-[80px]",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.button(
                                            rx.icon(tag="save", class_name="mr-2 h-4 w-4"),
                                            "Save Review",
                                            on_click=AdminState.save_review_results,
                                            class_name=rx.cond(
                                                AuthState.dark_mode,
                                                "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                                                "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                                            ),
                                        ),
                                        class_name="flex justify-end",
                                    ),
                                    class_name="space-y-2",
                                ),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "p-4 bg-white/5 border border-white/10 rounded-2xl mt-4 backdrop-blur",
                                    "p-4 bg-teal-50 border border-teal-200 rounded-2xl mt-4",
                                ),
                            ),
                            None,
                        ),
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                rx.icon(tag="x", class_name="h-4 w-4"),
                                class_name=rx.cond(
                                    AuthState.dark_mode,
                                    "absolute top-3 right-3 p-1 rounded-full text-slate-400 hover:bg-white/10",
                                    "absolute top-3 right-3 p-1 rounded-full text-slate-500 hover:bg-slate-100",
                                ),
                                on_click=ProposalState.close_detail_modal,
                            )
                        ),
                        class_name="space-y-4",
                    ),
                    rx.el.div("No proposal selected."),
                ),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-3xl max-h-[85vh] rounded-3xl border border-white/10 bg-slate-950/95 p-6 text-slate-100 shadow-2xl backdrop-blur-2xl overflow-y-auto",
                    "fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-3xl max-h-[85vh] rounded-3xl border border-white/60 bg-white p-6 text-slate-900 shadow-2xl backdrop-blur overflow-y-auto",
                ),
            ),
        ),
        open=ProposalState.show_detail_modal,
    )


def delete_confirmation_dialog() -> rx.Component:
    return rx.cond(
        ProposalState.show_delete_confirm,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Delete Proposal",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "text-lg font-semibold text-white",
                        "text-lg font-semibold text-slate-900",
                    ),
                ),
                rx.el.p(
                    "Deleting this proposal will remove all associated information and uploaded documents.",
                    class_name=rx.cond(
                        AuthState.dark_mode,
                        "mt-3 text-sm text-slate-300",
                        "mt-3 text-sm text-slate-700",
                    ),
                ),
                rx.cond(
                    ProposalState.pending_delete_proposal,
                    rx.el.p(
                        f'Proposal: {ProposalState.pending_delete_proposal["title"]}',
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "mt-2 text-sm font-semibold text-white",
                            "mt-2 text-sm font-semibold text-slate-900",
                        ),
                    ),
                    None,
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=ProposalState.cancel_delete_prompt,
                        class_name=rx.cond(
                            AuthState.dark_mode,
                            "inline-flex items-center rounded-md border border-white/20 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/20",
                            "inline-flex items-center rounded-md border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-200",
                        ),
                    ),
                    rx.el.button(
                        "Delete",
                        on_click=ProposalState.confirm_delete_proposal,
                        class_name="inline-flex items-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300",
                    ),
                    class_name="mt-6 flex items-center justify-end gap-3",
                ),
                class_name=rx.cond(
                    AuthState.dark_mode,
                    "space-y-2 rounded-2xl bg-slate-950/95 border border-white/10 p-6 shadow-2xl backdrop-blur w-[90vw] max-w-md",
                    "space-y-2 rounded-2xl bg-white border border-white/60 p-6 shadow-2xl w-[90vw] max-w-md",
                ),
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4",
        ),
        None,
    )
