import PageHeader from "../components/common/PageHeader";
import EmptyState from "../components/common/EmptyState";

export default function SettingsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Control"
        title="Settings"
        description="Account, security, notification, and preferences controls are ready for API-backed implementation."
      />

      <EmptyState
        title="Settings are not yet backed by a server contract"
        description="Only the authentication flow is currently live. The settings surface is staged for future account and security management."
      />
    </div>
  );
}
