import { Activity, ArrowUpRight, Cpu, FileText, ShieldCheck, Sparkles } from "lucide-react";

import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";

const summaryCards = [
  { label: "Tasks", value: "—", hint: "No task data yet" },
  { label: "AI Employees", value: "—", hint: "No agents connected" },
  { label: "Success Rate", value: "—", hint: "Connect analytics" },
  { label: "Running", value: "—", hint: "No active jobs" },
];

const feed = [
  { title: "Secure session", detail: "Authentication and token refresh are active." },
  { title: "Backend status", detail: "Real API endpoints are connected where available." },
  { title: "System state", detail: "Unsupported platform features are marked as coming soon." },
];

export default function Overview() {
  return (
    <div>
      <PageHeader
        eyebrow="System // 001"
        title="Good morning."
        description="Your KARYA operating layer is ready. Connect backend data sources to populate live workflow telemetry."
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => (
          <article key={card.label} className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-5">
            <div className="flex items-center justify-between text-[#8A8A85]">
              <span className="text-[10px] uppercase tracking-[0.2em]">{card.label}</span>
              <ArrowUpRight size={16} />
            </div>
            <div className="mt-6 text-3xl font-semibold text-[#F5F5F5]">{card.value}</div>
            <p className="mt-2 text-xs uppercase tracking-[0.2em] text-[#555550]">{card.hint}</p>
          </article>
        ))}
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <article className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="mb-5 flex items-center gap-3">
            <Cpu size={18} className="text-[#F5F5F5]" />
            <h2 className="text-xs uppercase tracking-[0.2em] text-[#F5F5F5]">Active AI Employees</h2>
          </div>

          <EmptyState
            title="No AI employee data available yet"
            description="The backend does not expose agent telemetry right now. This space will populate as agent endpoints are added."
          />
        </article>

        <article className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="mb-5 flex items-center gap-3">
            <Activity size={18} className="text-[#F5F5F5]" />
            <h2 className="text-xs uppercase tracking-[0.2em] text-[#F5F5F5]">Recent activity</h2>
          </div>

          <div className="space-y-4">
            {feed.map((item) => (
              <div key={item.title} className="rounded-xl border border-[#202020] bg-[#111111] p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-[#f43131]">{item.title}</div>
                <p className="mt-2 text-sm text-[#D8D8D8]">{item.detail}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="mt-8 grid gap-6 md:grid-cols-3">
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <Sparkles size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">System status</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">Authentication is active and the app is using the backend’s real auth flow.</p>
        </div>
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <FileText size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">Knowledge state</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">This workspace is ready for knowledge sources once the backend exposes them.</p>
        </div>
        <div className="rounded-2xl border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3 text-[#F5F5F5]">
            <ShieldCheck size={18} />
            <span className="text-xs uppercase tracking-[0.2em]">Security</span>
          </div>
          <p className="mt-5 text-sm text-[#8A8A85]">Secrets remain server-side and the frontend only communicates through the API layer.</p>
        </div>
      </section>
    </div>
  );
}
