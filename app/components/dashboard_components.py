import reflex as rx
import reflex as rx
from app.state import AuthState, Proposal
from app.states.proposal_state import ProposalState
from app.states.admin_state import AdminState


def dashboard_home() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Dashboard", class_name="text-3xl font-bold tracking-tight text-gray-900"
        ),
        rx.el.p(
            f"Welcome back, {AuthState.authenticated_user}!",
            class_name="mt-2 text-gray-600",
        ),
        rx.el.div(
            rx.el.h2("Recent Activity", class_name="text-xl font-semibold mb-4"),
            rx.el.p("No recent activity to display.", class_name="text-gray-500"),
            class_name="mt-8 p-6 bg-white rounded-lg border border-gray-200 shadow-sm",
        ),
    )


def _form_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    error: rx.Var[str],
    type: str = "text",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            placeholder=placeholder,
            default_value=value,
            on_change=on_change,
            type=type,
            class_name=rx.cond(
                error,
                "block w-full rounded-md border-red-300 bg-red-50 p-2 text-sm text-red-900 placeholder-red-400 transition-all duration-150 ease-in-out focus:border-red-500 focus:outline-none focus:ring-red-500",
                "block w-full rounded-md border-gray-300 bg-gray-50 p-2 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500",
            ),
        ),
        rx.cond(error, rx.el.p(error, class_name="mt-1 text-xs text-red-600"), None),
    )


def create_proposal_form() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            rx.cond(ProposalState.is_editing, "Edit Proposal", "Create New Proposal"),
            class_name="text-3xl font-bold tracking-tight text-gray-900",
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
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.textarea(
                        placeholder="Detailed description of your proposal...",
                        default_value=ProposalState.description,
                        on_change=ProposalState.set_description,
                        class_name="block w-full rounded-md border-gray-300 bg-gray-50 p-2 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500 min-h-[120px]",
                    ),
                    rx.cond(
                        ProposalState.description_error,
                        rx.el.p(
                            ProposalState.description_error,
                            class_name="mt-1 text-xs text-red-600",
                        ),
                        None,
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Proposal Document",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                tag="cloud_upload", class_name="h-8 w-8 text-gray-500"
                            ),
                            rx.el.p("Drag & drop or click to upload"),
                            rx.el.span(
                                "PDF, DOC, DOCX up to 10MB",
                                class_name="text-xs text-gray-500",
                            ),
                            class_name="flex flex-col items-center justify-center gap-1 border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:bg-gray-100",
                        ),
                        id="proposal_upload",
                        accept={
                            "application/pdf": [".pdf"],
                            "application/msword": [".doc"],
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                                ".docx"
                            ],
                        },
                        max_files=1,
                        class_name="w-full",
                    ),
                    rx.el.div(
                        rx.foreach(
                            rx.selected_files("proposal_upload"),
                            lambda file: rx.el.div(
                                rx.icon("file-text", class_name="h-4 w-4"),
                                file,
                                class_name="flex items-center gap-2 text-sm p-2 bg-gray-100 border rounded-md",
                            ),
                        )
                    ),
                    rx.cond(
                        ProposalState.proposal_file_error,
                        rx.el.p(
                            ProposalState.proposal_file_error,
                            class_name="mt-1 text-xs text-red-600",
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
                    class_name="flex-1 items-center justify-center rounded-lg bg-gradient-to-r from-teal-500 to-cyan-600 px-5 py-3 text-sm font-medium text-white shadow-md transition-all duration-150 ease-in-out hover:from-teal-600 hover:to-cyan-700 focus:outline-none focus:ring-4 focus:ring-teal-300 disabled:cursor-not-allowed disabled:opacity-50",
                ),
                rx.cond(
                    ProposalState.is_editing,
                    rx.el.button(
                        "Cancel",
                        type="button",
                        on_click=ProposalState.cancel_edit,
                        class_name="flex-1 items-center justify-center rounded-lg bg-gray-500 px-5 py-3 text-sm font-medium text-white shadow-md transition-all duration-150 ease-in-out hover:bg-gray-600 focus:outline-none focus:ring-4 focus:ring-gray-300",
                    ),
                    None,
                ),
                class_name="mt-8 flex gap-4 w-full",
            ),
            class_name="mt-8 max-w-2xl mx-auto p-8 bg-white rounded-lg border border-gray-200 shadow-sm",
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
                    proposal["title"], class_name="text-lg font-semibold text-gray-900"
                ),
                _status_badge(proposal["status"]),
                class_name="flex items-center justify-between",
            ),
            rx.el.p(
                f"Affiliation: {proposal['affiliation']}",
                class_name="text-sm text-gray-600 mt-1",
            ),
            rx.el.p(
                f"Submitted: {proposal['created_at'].to_string().replace('T', ' ').split('.')[0]}",
                class_name="text-sm text-gray-500 mt-1",
            ),
            class_name="flex-1",
        ),
        rx.el.button(
            "View Details",
            on_click=lambda: ProposalState.view_proposal_details(proposal),
            class_name="mt-4 sm:mt-0 sm:ml-4 px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 focus:ring-4 focus:outline-none focus:ring-teal-300",
        ),
        class_name="bg-white p-6 rounded-lg border border-gray-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between",
    )


def my_proposals_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "My Proposals",
                class_name="text-3xl font-bold tracking-tight text-gray-900 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(tag="search", class_name="h-5 w-5 text-gray-400"),
                    class_name="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3",
                ),
                rx.el.input(
                    placeholder="Search by title or description...",
                    on_change=ProposalState.set_search_query.debounce(300),
                    class_name="block w-full rounded-lg border border-gray-200 bg-gray-50 py-2.5 pl-10 pr-3 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500",
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
                class_name="rounded-lg border border-gray-200 bg-gray-50 py-2.5 pl-3 pr-8 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500",
            ),
            class_name="flex flex-col sm:flex-row items-center gap-4 mb-6",
        ),
        rx.el.div(
            rx.foreach(ProposalState.filtered_proposals, _proposal_card),
            class_name="space-y-4",
        ),
        proposal_detail_modal(),
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
                                class_name="text-xl font-bold text-gray-900",
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
                                class_name="text-sm text-gray-700",
                            ),
                            rx.el.div(
                                rx.el.h3("Affiliation", class_name="font-semibold"),
                                rx.el.p(ProposalState.selected_proposal["affiliation"]),
                                class_name="text-sm text-gray-700",
                            ),
                            rx.el.div(
                                rx.el.h3("Submitted On", class_name="font-semibold"),
                                rx.el.p(
                                    ProposalState.selected_proposal["created_at"]
                                    .to_string()
                                    .replace("T", " ")
                                    .split(".")[0]
                                ),
                                class_name="text-sm text-gray-700",
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Description", class_name="font-semibold mt-4 mb-2"
                            ),
                            rx.el.p(
                                ProposalState.selected_proposal["description"],
                                class_name="text-sm text-gray-700 bg-gray-50 p-3 rounded-md border",
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
                                    class_name="text-sm text-gray-700 bg-blue-50 p-3 rounded-md border border-blue-200",
                                ),
                            ),
                            None,
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon(tag="download", class_name="mr-2 h-4 w-4"),
                                "Download Document",
                                on_click=ProposalState.download_proposal_file,
                                class_name="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 focus:ring-4 focus:outline-none focus:ring-teal-300",
                            ),
                            rx.cond(
                                ProposalState.selected_proposal["user_email"]
                                == AuthState.authenticated_user,
                                rx.el.button(
                                    rx.icon(tag="copy", class_name="mr-2 h-4 w-4"),
                                    "Edit Proposal",
                                    on_click=ProposalState.load_proposal_for_edit,
                                    class_name="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300",
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
                                            AdminState.review_results_input,
                                        ),
                                        class_name="rounded-lg border border-gray-300 bg-gray-50 text-sm focus:border-teal-500 focus:ring-teal-500 w-full sm:w-auto mb-2",
                                    ),
                                    rx.el.textarea(
                                        placeholder="Add review results...",
                                        default_value=AdminState.review_results_input,
                                        on_change=AdminState.set_review_results_input,
                                        class_name="block w-full rounded-md border-gray-300 bg-gray-50 p-2 text-sm text-gray-800 transition-all duration-150 ease-in-out focus:border-teal-500 focus:outline-none focus:ring-teal-500 min-h-[80px]",
                                    ),
                                    class_name="space-y-2",
                                ),
                                class_name="p-4 bg-teal-50 border border-teal-200 rounded-lg mt-4",
                            ),
                            None,
                        ),
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                rx.icon(tag="x", class_name="h-4 w-4"),
                                class_name="absolute top-3 right-3 p-1 rounded-full text-gray-500 hover:bg-gray-100",
                                on_click=ProposalState.close_detail_modal,
                            )
                        ),
                        class_name="space-y-4",
                    ),
                    rx.el.div("No proposal selected."),
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-3xl max-h-[85vh] bg-white rounded-xl p-6 shadow-lg overflow-y-auto",
            ),
        ),
        open=ProposalState.show_detail_modal,
    )