import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function AgentsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="AI Workforce"
        title="AI Employees"
        description="The backend currently exposes auth and profile endpoints. Agent inventory will appear here when the service layer is available."
        action={<button type="button" className="rounded-xl border border-[#2A2A2A] bg-white px-4 py-2 text-xs uppercase tracking-[0.2em] text-black">Create employee</button>}
      />

      <EmptyState
        title="Agent directory unavailable"
        description="No agent API contract is available in the current backend, so this page is intentionally empty and ready for real integration."
      />
    </div>
  );
}
