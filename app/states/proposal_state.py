import reflex as rx
from app.state import AuthState, db, Proposal
import re
import uuid
import datetime
from pathlib import Path
from reflex.event import PointerEventInfo


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".hwp", ".hwpx"}


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
    refresh_token: str = ""
    show_delete_confirm: bool = False
    pending_delete_proposal: Proposal | None = None

    @rx.var
    def selected_proposal_files(self) -> list[str]:
        """Returns the file names associated with the selected proposal."""
        if self.selected_proposal:
            value = self.selected_proposal["proposal_file"]
            if isinstance(value, list):
                return [str(item) for item in value if item]
            if isinstance(value, str) and value:
                return [value]
        return []

    @rx.var
    def has_selected_proposal_files(self) -> bool:
        if self.selected_proposal:
            value = self.selected_proposal["proposal_file"]
            if isinstance(value, list):
                return any(value)
            if isinstance(value, str):
                return bool(value)
        return False

    @rx.var
    def proposal_summary(self) -> dict[str, int]:
        _ = self.refresh_token
        proposals = db.get_user_proposals(self.authenticated_user or "")
        summary = {
            "total": len(proposals),
            "submitted": 0,
            "under_review": 0,
            "approved": 0,
        }
        for proposal in proposals:
            status = proposal.get("status", "")
            if status == "Submitted":
                summary["submitted"] += 1
            elif status == "Under Review":
                summary["under_review"] += 1
            elif status == "Approved":
                summary["approved"] += 1
        return summary

    @rx.var
    def total_proposals_count(self) -> int:
        return self.proposal_summary["total"]

    @rx.var
    def under_review_count(self) -> int:
        return self.proposal_summary["under_review"]

    @rx.var
    def approved_count(self) -> int:
        return self.proposal_summary["approved"]

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
        upload = files[0]
        original_name = Path(getattr(upload, "name", "")).name
        if not original_name:
            self.proposal_file_error = "Invalid file upload."
            self.loading = False
            yield rx.toast.error("Unable to process the uploaded file.")
            return
        extension = Path(original_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ext.lstrip(".") for ext in ALLOWED_EXTENSIONS))
            self.proposal_file_error = f"Only the following file types are allowed: {allowed}."
            self.loading = False
            yield rx.toast.error("Unsupported file type uploaded.")
            return
        upload_data = await upload.read()
        if len(upload_data) > MAX_UPLOAD_SIZE_BYTES:
            self.proposal_file_error = "File exceeds the 50 MB size limit."
            self.loading = False
            yield rx.toast.error("Uploaded file is too large.")
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        safe_path = Path(original_name)
        unique_name = f"{safe_path.stem}_{timestamp}{safe_path.suffix}"
        file_path = rx.get_upload_dir() / unique_name
        try:
            with file_path.open("wb") as f:
                f.write(upload_data)
        except OSError:
            self.proposal_file_error = "Failed to save the uploaded file."
            self.loading = False
            yield rx.toast.error("Could not store the uploaded file.")
            return
        self.proposal_file = unique_name
        if not self._validate_form():
            self.loading = False
            self._remove_uploaded_file(unique_name)
            self.proposal_file = ""
            yield rx.toast.error("Please correct the errors in the form.")
            return
        timestamp = datetime.datetime.now().isoformat()
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
            created_at=timestamp,
            updated_at=timestamp,
            status="Submitted",
            review_results="",
        )
        db.add_proposal(new_proposal)
        self.refresh_token = datetime.datetime.now().isoformat()
        self.loading = False
        self._reset_proposal_form()
        yield rx.toast.success("Proposal submitted successfully!")
        yield self.set_active_page("my_proposals")

    @rx.event
    async def handle_update_proposal(self, files: list[rx.UploadFile]):
        self.loading = True
        yield
        if not self.edit_proposal_id:
            self.loading = False
            yield rx.toast.error("Proposal not found.")
            return
        current = db.get_proposal(self.edit_proposal_id)
        if (
            not current
            or current.get("user_email") != (self.authenticated_user or "")
        ):
            self.loading = False
            yield rx.toast.error("Proposal not found.")
            return
        if current.get("status") != "Submitted":
            self.loading = False
            yield rx.toast.error(
                "This proposal can no longer be edited because it is not in Submitted status."
            )
            return
        new_file_name = ""
        if files:
            upload = files[0]
            original_name = Path(getattr(upload, "name", "")).name
            if not original_name:
                self.proposal_file_error = "Invalid file upload."
                self.loading = False
                yield rx.toast.error("Unable to process the uploaded file.")
                return
            extension = Path(original_name).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                allowed = ", ".join(sorted(ext.lstrip(".") for ext in ALLOWED_EXTENSIONS))
                self.proposal_file_error = f"Only the following file types are allowed: {allowed}."
                self.loading = False
                yield rx.toast.error("Unsupported file type uploaded.")
                return
            upload_data = await upload.read()
            if len(upload_data) > MAX_UPLOAD_SIZE_BYTES:
                self.proposal_file_error = "File exceeds the 10 MB size limit."
                self.loading = False
                yield rx.toast.error("Uploaded file is too large.")
                return
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            safe_path = Path(original_name)
            unique_name = f"{safe_path.stem}_{timestamp}{safe_path.suffix}"
            file_path = rx.get_upload_dir() / unique_name
            try:
                with file_path.open("wb") as f:
                    f.write(upload_data)
            except OSError:
                self.proposal_file_error = "Failed to save the uploaded file."
                self.loading = False
                yield rx.toast.error("Could not store the uploaded file.")
                return
            new_file_name = unique_name
            self.proposal_file = unique_name
            self.proposal_file_error = ""
        else:
            self.proposal_file = current.get("proposal_file", "")
        if not self._validate_form():
            self.loading = False
            if new_file_name:
                self._remove_uploaded_file(new_file_name)
                self.proposal_file = current.get("proposal_file", "")
            yield rx.toast.error("Please correct the errors in the form.")
            return
        updated = False
        if self.edit_proposal_id:
            updated = db.update_proposal(
                self.edit_proposal_id,
                {
                    "full_name": self.full_name,
                    "email": self.proposal_email,
                    "affiliation": self.affiliation,
                    "phone_number": self.phone_number,
                    "title": self.title,
                    "description": self.description,
                    "proposal_file": self.proposal_file,
                },
            )
        self.loading = False
        if not updated:
            if new_file_name:
                self._remove_uploaded_file(new_file_name)
                self.proposal_file = current.get("proposal_file", "")
            yield rx.toast.error("Proposal not found.")
            return
        if new_file_name:
            old_file = current.get("proposal_file")
            if isinstance(old_file, str) and old_file and old_file != new_file_name:
                self._remove_uploaded_file(old_file)
        latest = db.get_proposal(self.edit_proposal_id)
        if latest:
            self.selected_proposal = latest
        self.refresh_token = datetime.datetime.now().isoformat()
        yield ProposalState.cancel_edit()
        yield rx.toast.success("Proposal updated successfully!")
        yield self.set_active_page("my_proposals")

    def _remove_uploaded_file(self, file_name: str):
        if not file_name:
            return
        upload_dir = rx.get_upload_dir()
        project_upload_dir = Path(__file__).resolve().parent.parent / "uploaded_files"
        candidate_paths = []
        for base in (upload_dir, project_upload_dir):
            try:
                candidate_paths.append((base / file_name).resolve())
            except Exception:
                continue
        seen_paths: set[Path] = set()
        for path in candidate_paths:
            if path in seen_paths:
                continue
            seen_paths.add(path)
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass

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
        rx.clear_selected_files("proposal_upload")

    @rx.event
    def load_proposal_for_edit(self):
        if not self.selected_proposal:
            return rx.toast.error("No proposal selected.")
        if self.selected_proposal.get("status") != "Submitted":
            return rx.toast.error(
                "This proposal cannot be edited because it is already under review."
            )
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

    @rx.event
    def start_new_proposal(self):
        """Prepare the state for creating a brand new proposal."""
        self.is_editing = False
        self.edit_proposal_id = ""
        self.selected_proposal = None
        self.show_detail_modal = False
        self._reset_proposal_form()
        self.active_page = "create_proposal"

    @rx.event
    def remove_selected_upload(self, event: PointerEventInfo | None = None):
        """Allow users to clear the currently selected upload before submission."""
        self.proposal_file = ""
        self.proposal_file_error = ""
        return rx.clear_selected_files("proposal_upload")

    @rx.event
    def prompt_delete_proposal(self, proposal_id: str):
        current = db.get_proposal(proposal_id)
        if not current or current.get("user_email") != (self.authenticated_user or ""):
            return rx.toast.error("You cannot delete this proposal.")
        if current.get("status") != "Submitted":
            return rx.toast.error(
                "Only proposals in Submitted status can be deleted."
            )
        self.pending_delete_proposal = current
        self.show_delete_confirm = True

    @rx.event
    def cancel_delete_prompt(self):
        self.pending_delete_proposal = None
        self.show_delete_confirm = False

    def _delete_proposal_internal(self, proposal_id: str):
        current = db.get_proposal(proposal_id)
        if not current or current.get("user_email") != (self.authenticated_user or ""):
            return rx.toast.error("You cannot delete this proposal.")
        if current.get("status") != "Submitted":
            return rx.toast.error(
                "Only proposals in Submitted status can be deleted."
            )
        deleted = db.delete_proposal(proposal_id)
        if not deleted:
            return rx.toast.error("Failed to delete the proposal.")
        file_name = current.get("proposal_file")
        if isinstance(file_name, str) and file_name:
            upload_dir = rx.get_upload_dir()
            project_upload_dir = Path(__file__).resolve().parent.parent / "uploaded_files"
            candidate_paths = []
            try:
                candidate_paths.append((upload_dir / file_name).resolve())
            except Exception:
                pass
            try:
                candidate_paths.append((project_upload_dir / file_name).resolve())
            except Exception:
                pass
            seen_paths = set()
            for path in candidate_paths:
                if path in seen_paths:
                    continue
                seen_paths.add(path)
                try:
                    if path.exists():
                        path.unlink()
                except OSError:
                    pass
        if self.selected_proposal and self.selected_proposal["id"] == proposal_id:
            self.selected_proposal = None
            self.show_detail_modal = False
        self.refresh_token = datetime.datetime.now().isoformat()
        return rx.toast.success("Proposal deleted successfully.")

    @rx.event
    def delete_proposal(self, proposal_id: str):
        result = self._delete_proposal_internal(proposal_id)
        if self.pending_delete_proposal and self.pending_delete_proposal["id"] == proposal_id:
            self.pending_delete_proposal = None
            self.show_delete_confirm = False
        return result

    @rx.event
    def confirm_delete_proposal(self):
        if not self.pending_delete_proposal:
            self.show_delete_confirm = False
            return rx.toast.error("Proposal not found.")
        proposal_id = self.pending_delete_proposal["id"]
        result = self._delete_proposal_internal(proposal_id)
        self.pending_delete_proposal = None
        self.show_delete_confirm = False
        return result

    @rx.var
    def filtered_proposals(self) -> list[Proposal]:
        """Filters proposals based on search query and status."""
        _ = self.refresh_token
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
        latest = db.get_proposal(proposal["id"])
        if latest and latest.get("user_email") == (self.authenticated_user or ""):
            self.selected_proposal = latest
            self.show_detail_modal = True
        else:
            self.selected_proposal = None
            self.show_detail_modal = False
            return rx.toast.error("Unable to load the latest proposal details.")

    @rx.event
    def close_detail_modal(self):
        """Closes the detail modal and resets the selected proposal."""
        self.show_detail_modal = False
        self.selected_proposal = None

    @rx.event
    def download_proposal_file(
        self, event: PointerEventInfo | None = None, filename: str | None = None
    ):
        """Downloads the proposal file for the selected proposal."""
        if self.selected_proposal:
            target = filename or self.selected_proposal["proposal_file"]
            if target:
                return rx.download(filename=target)

    @rx.event
    def refresh_proposals(self):
        if self.selected_proposal:
            latest = db.get_proposal(self.selected_proposal["id"])
            if latest and latest.get("user_email") == (self.authenticated_user or ""):
                self.selected_proposal = latest
            else:
                self.selected_proposal = None
                self.show_detail_modal = False
        self.refresh_token = datetime.datetime.now().isoformat()
        return rx.toast.success("Proposals refreshed from the latest data.")
