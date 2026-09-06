import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function ActivityPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Observability"
        title="Activity"
        description="Live runtime events will populate once the backend exposes task and audit stream data."
      />

      <EmptyState
        title="Activity stream unavailable"
        description="No activity or audit endpoint is currently exposed by the API, so this panel remains deliberately empty."
      />
    </div>
  );
}
