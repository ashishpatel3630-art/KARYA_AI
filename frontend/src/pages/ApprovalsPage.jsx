import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function ApprovalsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Governance"
        title="Approvals"
        description="Approval workflows are scaffolded for future enterprise controls and remain disabled until backend support exists."
      />

      <EmptyState
        title="Approval center is not connected"
        description="No approval endpoint is available in the current API, so approval actions are intentionally disabled and labeled as coming soon."
      />
    </div>
  );
}
