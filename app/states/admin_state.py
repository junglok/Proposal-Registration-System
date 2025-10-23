import reflex as rx
import datetime
from pathlib import Path
from typing import Any
from app.state import AuthState, db, Proposal
from app.states.proposal_state import ProposalState


class AdminState(AuthState):
    review_results_input: str = ""
    refresh_token: str = ""
    search_query: str = ""
    status_filter: str = "All"
    pending_search_query: str = ""
    admin_delete_dialog_open: bool = False
    admin_pending_delete: Proposal | None = None

    @rx.var
    def all_proposals(self) -> list[Proposal]:
        if not self.is_admin:
            return []
        _ = self.refresh_token
        return db.get_all_proposals()

    @rx.var
    def filtered_admin_proposals(self) -> list[Proposal]:
        if not self.is_admin:
            return []
        _ = self.refresh_token
        proposals = db.get_all_proposals()
        search_lower = self.search_query.lower()
        return [
            proposal
            for proposal in proposals
            if (self.status_filter == "All" or proposal["status"] == self.status_filter)
            and (
                search_lower in proposal["title"].lower()
                or search_lower in proposal["description"].lower()
                or search_lower in proposal["full_name"].lower()
                or search_lower in proposal["user_email"].lower()
            )
        ]

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_status_filter(self, value: str):
        self.status_filter = value

    @rx.event
    def on_search_input_change(self, value: str):
        self.pending_search_query = value

    @rx.event
    def apply_search_query(self, form_data: dict[str, Any]):
        value = (
            form_data.get("search", "") if isinstance(form_data, dict) else ""
        ).strip()
        if not value:
            value = self.pending_search_query.strip()
        self.search_query = value
        self.pending_search_query = value
        return rx.toast.success("Search applied.")

    def _delete_proposal_and_files(self, proposal_id: str) -> tuple[bool, str]:
        current = db.get_proposal(proposal_id)
        if not current:
            return False, "Proposal not found."
        deleted = db.delete_proposal(proposal_id)
        if not deleted:
            return False, "Failed to delete the proposal."
        file_name = current.get("proposal_file")
        if isinstance(file_name, str) and file_name:
            upload_dir = rx.get_upload_dir()
            project_upload_dir = (
                Path(__file__).resolve().parent.parent / "uploaded_files"
            )
            candidate_paths: list[Path] = []
            try:
                candidate_paths.append((upload_dir / file_name).resolve())
            except Exception:
                pass
            try:
                candidate_paths.append((project_upload_dir / file_name).resolve())
            except Exception:
                pass
            seen: set[Path] = set()
            for path in candidate_paths:
                if path in seen:
                    continue
                seen.add(path)
                try:
                    if path.exists():
                        path.unlink()
                except OSError:
                    pass
        self.refresh_token = datetime.datetime.now().isoformat()
        return True, "Proposal deleted successfully."

    @rx.event
    def prompt_delete_proposal_admin(self, proposal_id: str):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        proposal = db.get_proposal(proposal_id)
        if not proposal:
            return rx.toast.error("Proposal not found.")
        self.admin_pending_delete = proposal
        self.admin_delete_dialog_open = True

    @rx.event
    def cancel_delete_prompt_admin(self):
        self.admin_pending_delete = None
        self.admin_delete_dialog_open = False

    @rx.event
    async def confirm_delete_proposal_admin(self):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        if not self.admin_pending_delete:
            self.admin_delete_dialog_open = False
            return rx.toast.error("No proposal selected for deletion.")
        proposal_id = self.admin_pending_delete["id"]
        success, message = self._delete_proposal_and_files(proposal_id)
        proposal_state = await self.get_state(ProposalState)
        if success:
            if (
                proposal_state.selected_proposal
                and proposal_state.selected_proposal["id"] == proposal_id
            ):
                proposal_state.selected_proposal = None
                proposal_state.show_detail_modal = False
            self.admin_pending_delete = None
            self.admin_delete_dialog_open = False
            return rx.toast.success(message)
        self.admin_pending_delete = None
        self.admin_delete_dialog_open = False
        return rx.toast.error(message)

    @rx.event
    def set_review_results_input(self, value: str):
        self.review_results_input = value

    @rx.event
    async def update_proposal_status(
        self, proposal_id: str, status: str, review_results: str | None = None
    ):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        latest = db.get_proposal(proposal_id)
        if not latest:
            return rx.toast.error("Proposal not found.")
        review_value = (
            review_results
            if review_results is not None
            else latest.get("review_results", "")
        )
        updated = db.update_proposal_status(proposal_id, status, review_value)
        if not updated:
            return rx.toast.error("Proposal not found.")
        proposal_state = await self.get_state(ProposalState)
        refreshed = db.get_proposal(proposal_id)
        if refreshed:
            if (
                proposal_state.selected_proposal
                and proposal_state.selected_proposal["id"] == proposal_id
            ):
                proposal_state.selected_proposal = refreshed
            if refreshed["id"] == proposal_id:
                self.review_results_input = refreshed.get("review_results", "")
        return rx.toast.success("Status and review updated successfully!")

    @rx.event
    async def save_review_results(self):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        proposal_state = await self.get_state(ProposalState)
        if not proposal_state.selected_proposal:
            return rx.toast.error("No proposal selected.")
        proposal_id = proposal_state.selected_proposal["id"]
        latest = db.get_proposal(proposal_id)
        if not latest:
            return rx.toast.error("Proposal not found.")
        status = latest.get("status", "Submitted")
        updated = db.update_proposal_status(
            proposal_id, status, self.review_results_input
        )
        if not updated:
            return rx.toast.error("Proposal not found.")
        refreshed = db.get_proposal(proposal_id)
        if refreshed:
            proposal_state.selected_proposal = refreshed
        return rx.toast.success("Review results saved.")

    @rx.event
    async def view_proposal_details_admin(self, proposal_id: str):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        proposal_state = await self.get_state(ProposalState)
        selected = db.get_proposal(proposal_id)
        if not selected:
            return rx.toast.error("Proposal not found.")
        self.review_results_input = selected.get("review_results", "")
        proposal_state.selected_proposal = selected
        proposal_state.show_detail_modal = True

    @rx.event
    async def refresh_admin_data(self):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        self.refresh_token = datetime.datetime.now().isoformat()
        proposal_state = await self.get_state(ProposalState)
        if proposal_state.selected_proposal:
            latest = db.get_proposal(proposal_state.selected_proposal["id"])
            if latest:
                proposal_state.selected_proposal = latest
            else:
                proposal_state.selected_proposal = None
                proposal_state.show_detail_modal = False
        if (
            self.admin_pending_delete
            and not db.get_proposal(self.admin_pending_delete["id"])
        ):
            self.admin_pending_delete = None
            self.admin_delete_dialog_open = False
        return rx.toast.success("Admin data refreshed.")

    @rx.var
    def user_list(self) -> list[dict[str, str]]:
        if not self.is_admin:
            return []
        _ = self.refresh_token
        return db.list_users()

    @rx.var
    def user_count(self) -> int:
        return len(self.user_list)
