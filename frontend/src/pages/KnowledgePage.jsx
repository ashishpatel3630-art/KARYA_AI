import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function KnowledgePage() {
  return (
    <div>
      <PageHeader
        eyebrow="Memory"
        title="Knowledge"
        description="Knowledge sources and document indexing will appear here when a backend knowledge API is available."
        action={<button type="button" className="rounded-xl border border-[#2A2A2A] bg-white px-4 py-2 text-xs uppercase tracking-[0.2em] text-black">Add knowledge</button>}
      />

      <EmptyState
        title="Knowledge base not connected"
        description="The current backend does not expose document or knowledge endpoints, so this page stays intentionally disabled."
      />
    </div>
  );
}
