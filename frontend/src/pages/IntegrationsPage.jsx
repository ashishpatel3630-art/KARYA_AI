import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function IntegrationsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Connections"
        title="Integrations"
        description="Supported integrations are shown only when the backend exposes them; otherwise they are marked as coming soon."
      />

      <EmptyState
        title="No integrations are currently exposed"
        description="Gmail, Slack, Notion, REST API, and storage integrations will appear here when the backend adds support."
      />
    </div>
  );
}
