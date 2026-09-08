import { PlugZap } from "lucide-react";
import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function IntegrationsPage() {
  const { integrations, toggleIntegration } = useOperations();
  return <div><PageHeader eyebrow="Connections" title="Integrations" description="Runtime health is shared with system status, activity, and analytics." /><div className="grid gap-px border border-[#202020] bg-[#202020] md:grid-cols-2">{integrations.map((integration) => <article key={integration.id} className="bg-[#0A0A0A] p-6"><div className="flex items-start justify-between gap-4"><div className="flex items-center gap-3"><PlugZap size={18} /><div><h2 className="text-lg text-white">{integration.name}</h2><p className="mt-1 font-mono text-[9px] uppercase tracking-[0.16em] text-[#777772]">{integration.type}</p></div></div><span className="font-mono text-[9px] uppercase tracking-[0.16em] text-[#C8C8C3]">{integration.status}</span></div><p className="mt-8 text-sm text-[#777772]">Used by {integration.usedBy}</p><button type="button" onClick={() => toggleIntegration(integration.id)} className="mt-6 border border-[#2A2A2A] px-4 py-3 text-xs uppercase tracking-[0.16em] text-[#D8D8D8] hover:border-white">{integration.status === "CONNECTED" ? "Disconnect" : "Connect"}</button></article>)}</div></div>;
}
