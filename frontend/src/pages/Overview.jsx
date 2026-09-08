import { Activity, ArrowRight, FileText, ShieldCheck, Sparkles, Workflow } from "lucide-react";
import { Link } from "react-router-dom";

import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

const runtimeSystems = [
  { label: "AI core", detail: "Local model runtime", status: "READY" },
  { label: "Knowledge engine", detail: "Retrieval and evidence", status: "READY" },
  { label: "Agent runtime", detail: "Execution orchestration", status: "READY" },
  { label: "Tool runtime", detail: "Permissions and sandbox", status: "READY" },
];

const flow = [
  ["01", "Knowledge", "Sources become context"],
  ["02", "Agents", "Context becomes capability"],
  ["03", "Tasks", "Capability becomes execution"],
  ["04", "Evidence", "Execution becomes traceability"],
];

export default function Overview() {
  const { systemStatus, activities, tasks, workflows, approvals } = useOperations();
  return (
    <div>
      <PageHeader
        eyebrow="System // 001"
        title="Good morning."
        description="The sovereign operating layer is ready. Move from knowledge to accountable execution."
      />

      <section className="border-y border-[#202020] bg-[#0A0A0A]">
        <div className="grid gap-px bg-[#202020] md:grid-cols-2 xl:grid-cols-4">
          {runtimeSystems.map((system) => (
            <article key={system.label} className="bg-[#0A0A0A] p-5">
              <div className="flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.2em] text-[#777772]">
                <span>{system.label}</span>
                <span className="text-[#F5F5F5]">{system.label === "Agent runtime" && systemStatus.system === "DEGRADED" ? "DEGRADED" : system.status}</span>
              </div>
              <p className="mt-8 text-sm text-[#D8D8D8]">{system.detail}</p>
              <div className="mt-5 h-px bg-[#2A2A2A]"><div className="h-px w-4/5 bg-white" /></div>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-10 grid gap-8 xl:grid-cols-[1.35fr_0.65fr]">
        <article className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8">
          <div className="flex items-center justify-between border-b border-[#202020] pb-5">
            <div className="flex items-center gap-3"><Workflow size={18} /><h2 className="text-xs uppercase tracking-[0.2em]">Execution model</h2></div>
            <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#555550]">KARYA // FLOW</span>
          </div>
          <div className="mt-8 grid gap-0 md:grid-cols-4">
            {flow.map(([number, label, detail], index) => (
              <div key={label} className="relative border-l border-[#2A2A2A] px-5 py-2 first:border-l-0 first:pl-0">
                {index < flow.length - 1 && <span className="absolute right-0 top-6 hidden w-5 border-t border-[#555550] md:block" />}
                <span className="font-mono text-[9px] text-[#777772]">{number}</span>
                <h3 className="mt-7 text-lg text-[#F5F5F5]">{label}</h3>
                <p className="mt-2 text-xs leading-5 text-[#777772]">{detail}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="border border-[#202020] bg-[#0A0A0A] p-6 sm:p-8">
          <div className="flex items-center gap-3"><Activity size={18} /><h2 className="text-xs uppercase tracking-[0.2em]">Attention queue</h2></div>
          <div className="mt-8 border-y border-[#202020] py-6">
            <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-[#777772]">{systemStatus.pendingApprovals} APPROVALS PENDING · {tasks.filter((task) => task.status === "RUNNING").length} TASKS RUNNING</p>
            <p className="mt-4 text-sm leading-6 text-[#D8D8D8]">{activities[0]?.description || "No live runtime events recorded."}</p>
          </div>
          <Link to="/app/activity" className="mt-6 inline-flex items-center gap-3 font-mono text-[9px] uppercase tracking-[0.18em] text-white hover:text-[#C8C8C3]">Open activity <ArrowRight size={14} /></Link>
        </article>
      </section>

      <section className="mt-8 grid gap-6 md:grid-cols-3">
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <Sparkles size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">System status</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">{systemStatus.secureSession ? "Secure session active through the existing authentication service." : "Secure session requires attention."}</p>
        </div>
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <FileText size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">Knowledge state</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">{workflows.length} workflows can use indexed sources from the shared knowledge layer.</p>
        </div>
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <ShieldCheck size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">Security</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">{approvals.length} approval records are tracked through the human-control layer.</p>
        </div>
      </section>
    </div>
  );
}
