import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function AnalyticsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Performance"
        title="Analytics"
        description="Operational metrics are intentionally hidden until the backend exposes real analytics data."
      />

      <EmptyState
        title="Analytics data not available yet"
        description="Connect an analytics source or expose metrics endpoints to populate this dashboard with execution data."
      />
    </div>
  );
}
