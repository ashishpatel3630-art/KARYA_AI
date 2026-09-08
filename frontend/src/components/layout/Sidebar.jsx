import {
  Activity,
  BriefcaseBusiness,
  Cpu,
  FileText,
  House,
  KeyRound,
  Layers3,
  Settings,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useOperations } from "../../context/OperationsContext";

const navItems = [
  { to: "/app", label: "Overview", icon: House },
  { to: "/app/agents", label: "AI Employees", icon: Cpu },
  { to: "/app/workflows", label: "Workflows", icon: Workflow },
  { to: "/app/tasks", label: "Tasks", icon: BriefcaseBusiness },
  { to: "/app/knowledge", label: "Knowledge", icon: FileText },
  { to: "/app/integrations", label: "Integrations", icon: Layers3 },
  { to: "/app/activity", label: "Activity", icon: Activity },
  { to: "/app/approvals", label: "Approvals", icon: ShieldCheck },
  { to: "/app/analytics", label: "Analytics", icon: Sparkles },
  { to: "/app/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const { agents, tasks, workflows, systemStatus } = useOperations();
  const counts = {
    "AI Employees": agents.length,
    Workflows: workflows.length,
    Tasks: tasks.length,
    Approvals: systemStatus.pendingApprovals,
  };

  return (
    <aside className="hidden w-72 shrink-0 border-r border-[#202020] bg-[#0A0A0A] lg:flex lg:flex-col">
      <div className="flex items-center gap-3 border-b border-[#202020] px-6 py-5">
        <div className="flex h-8 w-8 items-center justify-center border border-[#2A2A2A] bg-[#111111] text-[10px] uppercase tracking-[0.2em] text-[#F5F5F5]">
          K
        </div>
        <div>
          <div className="text-[10px] uppercase tracking-[0.35em] text-[#8A8A85]">KARYA</div>
          <div className="mt-1 text-[10px] uppercase tracking-[0.2em] text-[#555550]">Operating system</div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                isActive
                  ? "bg-white text-black"
                  : "text-[#D8D8D8] hover:bg-[#111111] hover:text-white"
              }`
            }
          >
            <Icon size={16} />
            <span className="min-w-0 flex-1">{label}</span>
            {counts[label] !== undefined && <span className="font-mono text-[10px] text-[#777772]">{counts[label]}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-[#202020] p-4">
        <div className="flex items-center gap-3 rounded-xl border border-[#2A2A2A] bg-[#111111] p-3 text-sm text-[#D8D8D8]">
          <KeyRound size={16} className="text-[#8A8A85]" />
          <span>API gateway</span>
        </div>
      </div>
    </aside>
  );
}
