import reflex as rx
from app.state import AuthState, db, Proposal
import re
import uuid
import datetime


class ProposalState(AuthState):
    full_name: str = ""
    proposal_email: str = ""
    affiliation: str = ""
    phone_number: str = ""
    title: str = ""
    description: str = ""
    proposal_file: str = ""
    full_name_error: str = ""
    proposal_email_error: str = ""
    affiliation_error: str = ""
    phone_number_error: str = ""
    title_error: str = ""
    description_error: str = ""
    proposal_file_error: str = ""
    loading: bool = False
    search_query: str = ""
    status_filter: str = "All"
    show_detail_modal: bool = False
    selected_proposal: Proposal | None = None
    is_editing: bool = False
    edit_proposal_id: str = ""

    def _validate_form(self) -> bool:
        self.full_name_error = "" if self.full_name else "Full name is required."
        self.proposal_email_error = (
            ""
            if re.match("[^@]+@[^@]+\\.[^@]+", self.proposal_email)
            else "Invalid email address."
        )
        self.affiliation_error = "" if self.affiliation else "Affiliation is required."
        self.phone_number_error = (
            "" if self.phone_number else "Phone number is required."
        )
        self.title_error = "" if self.title else "Proposal title is required."
        self.description_error = "" if self.description else "Description is required."
        if not self.is_editing:
            self.proposal_file_error = (
                "" if self.proposal_file else "A proposal document is required."
            )
        return not any(
            [
                self.full_name_error,
                self.proposal_email_error,
                self.affiliation_error,
                self.phone_number_error,
                self.title_error,
                self.description_error,
                self.proposal_file_error,
            ]
        )

    @rx.event
    async def handle_create_proposal(self, files: list[rx.UploadFile]):
        self.loading = True
        yield
        if not files:
            self.proposal_file_error = "A proposal document is required."
            self.loading = False
            yield rx.toast.error("Please upload a proposal document.")
            return
        upload_data = await files[0].read()
        file_path = rx.get_upload_dir() / files[0].name
        with file_path.open("wb") as f:
            f.write(upload_data)
        self.proposal_file = files[0].name
        if not self._validate_form():
            self.loading = False
            yield rx.toast.error("Please correct the errors in the form.")
            return
        new_proposal = Proposal(
            id=str(uuid.uuid4()),
            user_email=self.authenticated_user or "",
            full_name=self.full_name,
            email=self.proposal_email,
            affiliation=self.affiliation,
            phone_number=self.phone_number,
            title=self.title,
            description=self.description,
            proposal_file=self.proposal_file,
            created_at=datetime.datetime.now().isoformat(),
            status="Submitted",
            review_results="",
        )
        db.add_proposal(new_proposal)
        self.loading = False
        self._reset_proposal_form()
        yield rx.toast.success("Proposal submitted successfully!")
        yield self.set_active_page("my_proposals")

    @rx.event
    async def handle_update_proposal(self, files: list[rx.UploadFile]):
        self.loading = True
        yield
        if files:
            upload_data = await files[0].read()
            file_path = rx.get_upload_dir() / files[0].name
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.proposal_file = files[0].name
            self.proposal_file_error = ""
        if not self._validate_form():
            self.loading = False
            yield rx.toast.error("Please correct the errors in the form.")
            return
        if self.edit_proposal_id in db.proposals:
            db.proposals[self.edit_proposal_id].update(
                {
                    "full_name": self.full_name,
                    "email": self.proposal_email,
                    "affiliation": self.affiliation,
                    "phone_number": self.phone_number,
                    "title": self.title,
                    "description": self.description,
                    "proposal_file": self.proposal_file,
                }
            )
        self.loading = False
        yield ProposalState.cancel_edit()
        yield rx.toast.success("Proposal updated successfully!")
        yield self.set_active_page("my_proposals")

    def _reset_proposal_form(self):
        self.full_name = ""
        self.proposal_email = ""
        self.affiliation = ""
        self.phone_number = ""
        self.title = ""
        self.description = ""
        self.proposal_file = ""
        self.full_name_error = ""
        self.proposal_email_error = ""
        self.affiliation_error = ""
        self.phone_number_error = ""
        self.title_error = ""
        self.description_error = ""
        self.proposal_file_error = ""

    @rx.event
    def load_proposal_for_edit(self):
        if self.selected_proposal:
            self.is_editing = True
            self.edit_proposal_id = self.selected_proposal["id"]
            self.full_name = self.selected_proposal["full_name"]
            self.proposal_email = self.selected_proposal["email"]
            self.affiliation = self.selected_proposal["affiliation"]
            self.phone_number = self.selected_proposal["phone_number"]
            self.title = self.selected_proposal["title"]
            self.description = self.selected_proposal["description"]
            self.proposal_file = self.selected_proposal["proposal_file"]
            self.show_detail_modal = False
            return self.set_active_page("create_proposal")

    @rx.event
    def cancel_edit(self):
        self.is_editing = False
        self.edit_proposal_id = ""
        self._reset_proposal_form()
        return self.set_active_page("my_proposals")

    @rx.var
    def filtered_proposals(self) -> list[Proposal]:
        """Filters proposals based on search query and status."""
        proposals = db.get_user_proposals(self.authenticated_user or "")
        search_lower = self.search_query.lower()
        return [
            p
            for p in proposals
            if (self.status_filter == "All" or p["status"] == self.status_filter)
            and (
                search_lower in p["title"].lower()
                or search_lower in p["description"].lower()
            )
        ]

    @rx.event
    def view_proposal_details(self, proposal: Proposal):
        """Sets the selected proposal and shows the detail modal."""
        self.selected_proposal = proposal
        self.show_detail_modal = True

    @rx.event
    def close_detail_modal(self):
        """Closes the detail modal and resets the selected proposal."""
        self.show_detail_modal = False
        self.selected_proposal = None

    @rx.event
    def download_proposal_file(self):
        """Downloads the proposal file for the selected proposal."""
        if self.selected_proposal:
            return rx.download(filename=self.selected_proposal["proposal_file"])