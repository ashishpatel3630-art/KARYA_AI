import { Play, Plus, Settings2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function AgentsPage() {
  const { agents, createAgent, createTask } = useOperations();
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");

  function submitAgent(event) {
    event.preventDefault();
    if (!name.trim()) return;
    createAgent({ name: name.trim(), role: "Industrial operations", tools: ["Knowledge search"] });
    setName("");
    setCreating(false);
  }

  return (
    <div>
      <PageHeader eyebrow="AI Workforce" title="AI Employees" description="Agents connect knowledge, tools, tasks, and workflows into an accountable digital workforce." action={<button type="button" onClick={() => setCreating((value) => !value)} className="inline-flex items-center gap-2 border border-[#2A2A2A] bg-white px-4 py-3 text-xs uppercase tracking-[0.18em] text-black"><Plus size={15} /> Create agent</button>} />
      {creating && <form onSubmit={submitAgent} className="mb-8 border border-[#2A2A2A] bg-[#0A0A0A] p-5"><label className="block text-xs uppercase tracking-[0.18em] text-[#777772]">Agent name<input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Reliability Agent" className="mt-3 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none focus:border-white" /></label><div className="mt-4 flex justify-end"><button className="border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.18em] text-black">Create agent</button></div></form>}
      <div className="grid gap-px border border-[#202020] bg-[#202020] md:grid-cols-2">
        {agents.map((agent) => <article key={agent.id} className="bg-[#0A0A0A] p-6 sm:p-8"><div className="flex items-start justify-between gap-4"><div><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">{agent.role}</p><h2 className="mt-3 text-2xl text-[#F5F5F5]">{agent.name}</h2></div><span className="flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.18em] text-[#C8C8C3]"><span className="h-1.5 w-1.5 bg-white" />{agent.status}</span></div><div className="mt-8 grid grid-cols-2 gap-px border border-[#202020] bg-[#202020] sm:grid-cols-4">{[["Tasks", agent.taskCount], ["Workflows", agent.workflowCount], ["Knowledge", agent.knowledgeCount], ["Success", `${agent.successRate}%`]].map(([label, value]) => <div key={label} className="bg-[#111111] p-3"><p className="font-mono text-[8px] uppercase tracking-[0.16em] text-[#555550]">{label}</p><p className="mt-3 text-lg text-white">{value}</p></div>)}</div><div className="mt-6 flex flex-wrap gap-3"><button type="button" onClick={() => createTask({ title: `Run ${agent.name}`, agentId: agent.id })} className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black"><Play size={14} /> Run task</button><Link to="/app/tasks" className="inline-flex items-center gap-2 border border-[#2A2A2A] px-4 py-3 text-xs uppercase tracking-[0.16em] text-[#D8D8D8] hover:border-white"><Settings2 size={14} /> View tasks</Link></div></article>)}
      </div>
    </div>
  );
}
