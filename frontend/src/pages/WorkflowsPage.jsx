import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function WorkflowsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Automation"
        title="Workflows"
        description="The workflow builder is scaffolded for later node-based orchestration and remains disabled until backend support exists."
        action={<button type="button" className="rounded-xl border border-[#2A2A2A] bg-white px-4 py-2 text-xs uppercase tracking-[0.2em] text-black">Create workflow</button>}
      />

      <EmptyState
        title="No workflow API contract found"
        description="This page is ready for trigger → employee → action orchestration once the backend exposes workflow endpoints."
      />
    </div>
  );
}
