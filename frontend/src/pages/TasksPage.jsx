import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function TasksPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Execution"
        title="Tasks"
        description="Task telemetry is not available in the current backend API surface, so this view is intentionally aligned to future task data."
      />

      <EmptyState
        title="Task center is waiting for backend data"
        description="Use this space for running, waiting, completed, and failed tasks once a task service is exposed."
      />
    </div>
  );
}
