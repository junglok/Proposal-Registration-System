import reflex as rx
from app.states.admin_state import AdminState
from app.state import Proposal
from app.components.dashboard_components import proposal_detail_modal


def _admin_proposal_card(proposal: Proposal) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                proposal["title"], class_name="text-md font-semibold text-gray-800"
            ),
            rx.el.p(
                f"By: {proposal['full_name']} ({proposal['user_email']})",
                class_name="text-sm text-gray-500",
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
                    proposal["id"], status, proposal["review_results"]
                ),
                class_name="rounded-lg border border-gray-300 bg-gray-50 text-sm focus:border-teal-500 focus:ring-teal-500",
            ),
            rx.el.button(
                "View Details",
                on_click=lambda: AdminState.view_proposal_details_admin(proposal),
                class_name="px-3 py-1.5 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 focus:ring-4 focus:outline-none focus:ring-teal-300",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex items-center justify-between",
    )


def admin_panel() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Admin Panel",
            class_name="text-3xl font-bold tracking-tight text-gray-900 mb-6",
        ),
        rx.el.div(
            rx.foreach(AdminState.all_proposals, _admin_proposal_card),
            class_name="space-y-4",
        ),
        proposal_detail_modal(),
    )