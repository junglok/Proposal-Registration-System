import reflex as rx
from app.states.admin_state import AdminState
from app.state import Proposal, AuthState
from app.components.dashboard_components import proposal_detail_modal


def _admin_proposal_card(proposal: Proposal) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                proposal["title"],
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "text-md font-semibold text-white",
                    "text-md font-semibold text-slate-800",
                ),
            ),
            rx.el.p(
                f"By: {proposal['full_name']} ({proposal['user_email']})",
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "text-sm text-slate-300",
                    "text-sm text-slate-500",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    f"Created: {proposal['created_at'].replace('T', ' ')[:19]}",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-[11px] text-slate-400",
                        "text-[11px] text-slate-500",
                    ),
                ),
                rx.el.p(
                    f"Updated: {proposal.get('updated_at', proposal['created_at']).replace('T', ' ')[:19]}",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-[11px] text-slate-400",
                        "text-[11px] text-slate-500",
                    ),
                ),
                class_name="mt-1 space-y-1",
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Submitted", value="Submitted"),
                rx.el.option("Under Review", value="Under Review"),
                rx.el.option("Approved", value="Approved"),
                rx.el.option("Rejected", value="Rejected"),
                default_value=proposal["status"],
                on_change=lambda status: AdminState.update_proposal_status(
                    proposal["id"], status
                ),
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "rounded-xl border border-white/10 bg-white/5 text-sm text-slate-100 focus:border-cyan-400/80 focus:ring-cyan-400/40",
                    "rounded-xl border border-slate-200 bg-white text-sm text-slate-800 focus:border-cyan-500 focus:ring-cyan-500/40",
                ),
            ),
            rx.el.button(
                "View Details",
                on_click=lambda _: AdminState.view_proposal_details_admin(proposal["id"]),
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "px-3 py-1.5 text-sm font-semibold text-slate-900 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 shadow transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                    "px-3 py-1.5 text-sm font-semibold text-white rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 shadow transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                ),
            ),
            rx.el.button(
                "Delete",
                on_click=lambda _: AdminState.prompt_delete_proposal_admin(proposal["id"]),
                class_name="px-3 py-1.5 text-sm font-semibold text-white rounded-full bg-red-500 shadow hover:bg-red-600 focus:outline-none focus:ring-4 focus:ring-red-200/60",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name=rx.cond(
            AdminState.dark_mode,
            "flex items-center justify-between gap-4 rounded-3xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur",
            "flex items-center justify-between gap-4 rounded-3xl border border-white/60 bg-white p-4 shadow-lg",
        ),
    )


def _user_card(user: dict[str, rx.Var | str]) -> rx.Component:
    email = user.get("email", "")
    created_label = user.get("created_label", "N/A")
    is_admin = user.get("is_admin", False)

    badge_text = rx.cond(is_admin, "ADMIN", "USER")
    badge_class = rx.cond(
        AuthState.dark_mode,
        rx.cond(
            is_admin,
            "px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-full bg-cyan-400/15 text-cyan-200",
            "px-2 py-0.5 text-[10px] font-medium tracking-wide uppercase rounded-full bg-white/10 text-slate-200",
        ),
        rx.cond(
            is_admin,
            "px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-full bg-cyan-100 text-cyan-700",
            "px-2 py-0.5 text-[10px] font-medium tracking-wide uppercase rounded-full bg-slate-100 text-slate-600",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.icon(
                tag="user",
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "h-10 w-10 rounded-full bg-white/10 p-2 text-cyan-200",
                    "h-10 w-10 rounded-full bg-cyan-100 p-2 text-cyan-600",
                ),
            ),
            rx.el.div(
                rx.el.span(
                    email,
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-sm font-semibold text-white",
                        "text-sm font-semibold text-slate-900",
                    ),
                ),
                rx.el.span(
                    "Joined: ",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-xs text-slate-300",
                        "text-xs text-slate-500",
                    ),
                ),
                rx.el.span(
                    created_label,
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-xs text-slate-200",
                        "text-xs text-slate-600",
                    ),
                ),
                class_name="flex flex-col",
            ),
            rx.el.span(badge_text, class_name=badge_class),
            class_name="flex items-start justify-between gap-3",
        ),
        class_name=rx.cond(
            AdminState.dark_mode,
            "rounded-3xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur",
            "rounded-3xl border border-white/60 bg-white p-4 shadow",
        ),
    )


def admin_panel() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Admin Panel",
            class_name=rx.cond(
                AdminState.dark_mode,
                "text-3xl font-semibold tracking-tight text-white mb-6",
                "text-3xl font-semibold tracking-tight text-slate-900 mb-6",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        tag="search",
                        class_name=rx.cond(
                            AdminState.dark_mode,
                            "h-5 w-5 text-slate-400",
                            "h-5 w-5 text-slate-400",
                        ),
                    ),
                    class_name="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3",
                ),
                rx.el.form(
                    rx.el.input(
                        placeholder="Search by title, description, or user...",
                        value=AdminState.pending_search_query,
                        on_change=AdminState.on_search_input_change,
                        name="search",
                        class_name=rx.cond(
                            AdminState.dark_mode,
                            "block w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-3 text-sm text-slate-100 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                            "block w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-800 transition focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                        ),
                    ),
                    rx.el.button(
                        "Apply",
                        type="submit",
                        class_name="hidden",
                    ),
                    on_submit=AdminState.apply_search_query,
                    class_name="w-full",
                ),
                class_name="relative flex-grow",
            ),
            rx.el.select(
                rx.el.option("All Statuses", value="All"),
                rx.el.option("Submitted", value="Submitted"),
                rx.el.option("Under Review", value="Under Review"),
                rx.el.option("Approved", value="Approved"),
                rx.el.option("Rejected", value="Rejected"),
                on_change=AdminState.set_status_filter,
                value=AdminState.status_filter,
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "rounded-xl border border-white/10 bg-white/5 py-2.5 pl-3 pr-8 text-sm text-slate-100 transition focus:border-cyan-400/80 focus:outline-none focus:ring-2 focus:ring-cyan-400/30",
                    "rounded-xl border border-slate-200 bg-white py-2.5 pl-3 pr-8 text-sm text-slate-800 transition focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30",
                ),
            ),
            rx.el.button(
                rx.icon(tag="refresh_cw", class_name="mr-2 h-4 w-4"),
                "Refresh",
                on_click=AdminState.refresh_admin_data,
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg transition hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                    "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                ),
            ),
            class_name="flex flex-col sm:flex-row items-center gap-4 mb-6",
        ),
        rx.el.div(
            rx.foreach(AdminState.filtered_admin_proposals, _admin_proposal_card),
            class_name="space-y-4",
        ),
        proposal_detail_modal(),
        admin_delete_confirmation_dialog(),
    )


def user_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "User Directory",
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "text-3xl font-semibold tracking-tight text-white",
                    "text-3xl font-semibold tracking-tight text-slate-900",
                ),
            ),
            rx.el.p(
                "Review who has access to the application and when they joined.",
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "text-sm text-slate-300 mt-2",
                    "text-sm text-slate-600 mt-2",
                ),
            ),
            class_name="flex flex-col gap-2 mb-6",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon(tag="refresh_cw", class_name="mr-2 h-4 w-4"),
                "Refresh",
                on_click=AdminState.refresh_admin_data,
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "inline-flex items-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:from-cyan-300 hover:to-indigo-400 focus:outline-none focus:ring-4 focus:ring-cyan-300/40",
                    "inline-flex items-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-4 focus:ring-teal-300/40",
                ),
            ),
            class_name="flex justify-end mb-6",
        ),
        rx.cond(
            AdminState.user_count > 0,
            rx.el.div(
                rx.foreach(AdminState.user_list, _user_card),
                class_name="grid gap-4 sm:grid-cols-2 xl:grid-cols-3",
            ),
            rx.el.div(
                rx.icon(tag="users", class_name="h-12 w-12 text-slate-400 mb-4"),
                rx.el.p(
                    "No users found.",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-sm text-slate-300",
                        "text-sm text-slate-600",
                    ),
                ),
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "flex flex-col items-center justify-center rounded-3xl border border-white/10 bg-white/5 p-10 text-center backdrop-blur",
                    "flex flex-col items-center justify-center rounded-3xl border border-white/60 bg-white p-10 text-center",
                ),
            ),
        ),
    )

def admin_delete_confirmation_dialog() -> rx.Component:
    return rx.cond(
        AdminState.admin_delete_dialog_open,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Delete Proposal",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "text-lg font-semibold text-white",
                        "text-lg font-semibold text-slate-900",
                    ),
                ),
                rx.el.p(
                    "Deleting this proposal will remove all associated information and uploaded documents.",
                    class_name=rx.cond(
                        AdminState.dark_mode,
                        "mt-3 text-sm text-slate-300",
                        "mt-3 text-sm text-slate-700",
                    ),
                ),
                rx.cond(
                    AdminState.admin_pending_delete,
                    rx.el.p(
                        f'Proposal: {AdminState.admin_pending_delete["title"]}',
                        class_name=rx.cond(
                            AdminState.dark_mode,
                            "mt-2 text-sm font-semibold text-white",
                            "mt-2 text-sm font-semibold text-slate-900",
                        ),
                    ),
                    None,
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=AdminState.cancel_delete_prompt_admin,
                        class_name=rx.cond(
                            AdminState.dark_mode,
                            "inline-flex items-center rounded-md border border-white/20 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/20",
                            "inline-flex items-center rounded-md border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-200",
                        ),
                    ),
                    rx.el.button(
                        "Delete",
                        on_click=AdminState.confirm_delete_proposal_admin,
                        class_name="inline-flex items-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300",
                    ),
                    class_name="mt-6 flex items-center justify-end gap-3",
                ),
                class_name=rx.cond(
                    AdminState.dark_mode,
                    "space-y-2 rounded-2xl bg-slate-900/90 p-6 shadow-2xl backdrop-blur text-white w-[90vw] max-w-md border border-white/10",
                    "space-y-2 rounded-2xl bg-white p-6 shadow-2xl w-[90vw] max-w-md border border-white/60",
                ),
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4",
        ),
        None,
    )
