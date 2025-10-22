import reflex as rx
from app.state import AuthState, db, Proposal
from app.states.proposal_state import ProposalState


class AdminState(AuthState):
    review_results_input: str = ""

    @rx.var
    def all_proposals(self) -> list[Proposal]:
        if not self.is_admin:
            return []
        return sorted(
            list(db.proposals.values()), key=lambda p: p["created_at"], reverse=True
        )

    @rx.event
    def update_proposal_status(
        self, proposal_id: str, status: str, review_results: str
    ):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        if proposal_id in db.proposals:
            db.proposals[proposal_id]["status"] = status
            db.proposals[proposal_id]["review_results"] = review_results
            proposal_state = self.get_state_sync(ProposalState)
            if (
                proposal_state.selected_proposal
                and proposal_state.selected_proposal["id"] == proposal_id
            ):
                proposal_state.selected_proposal = db.proposals[proposal_id]
            return rx.toast.success(f"Status and review updated successfully!")
        return rx.toast.error("Proposal not found.")

    @rx.event
    async def view_proposal_details_admin(self, proposal: Proposal):
        if not self.is_admin:
            return rx.toast.error("You are not authorized to perform this action.")
        proposal_state = await self.get_state(ProposalState)
        self.review_results_input = proposal.get("review_results", "")
        proposal_state.selected_proposal = proposal
        proposal_state.show_detail_modal = True