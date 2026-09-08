import { Ban, Play, Plus, RotateCcw } from "lucide-react";
import { useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function TasksPage() {
  const { tasks, agents, createTask, runTask, cancelTask } = useOperations();
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [filter, setFilter] = useState("ALL");
  const visibleTasks = filter === "ALL" ? tasks : tasks.filter((task) => task.status === filter);

  function submitTask(event) {
    event.preventDefault();
    if (!title.trim()) return;
    createTask({ title: title.trim(), agentId: agents[0]?.id });
    setTitle("");
    setCreating(false);
  }

  return <div><PageHeader eyebrow="Execution" title="Tasks" description="Every task keeps its agent, workflow, evidence, status, and activity context." action={<button type="button" onClick={() => setCreating((value) => !value)} className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.18em] text-black"><Plus size={15} /> Create task</button>} />
    {creating && <form onSubmit={submitTask} className="mb-8 border border-[#2A2A2A] bg-[#0A0A0A] p-5"><label className="block text-xs uppercase tracking-[0.18em] text-[#777772]">Task title<input autoFocus value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Describe the work to execute" className="mt-3 w-full border border-[#2A2A2A] bg-[#050505] px-4 py-3 text-sm text-white outline-none focus:border-white" /></label><div className="mt-4 flex justify-end"><button className="border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.18em] text-black">Queue task</button></div></form>}
    <div className="mb-5 flex flex-wrap gap-2">{["ALL", "QUEUED", "RUNNING", "WAITING", "COMPLETED", "CANCELLED"].map((status) => <button key={status} type="button" onClick={() => setFilter(status)} className={`border px-3 py-2 font-mono text-[9px] uppercase tracking-[0.16em] ${filter === status ? "border-white bg-white text-black" : "border-[#2A2A2A] text-[#777772] hover:text-white"}`}>{status}</button>)}</div>
    <div className="space-y-3">{visibleTasks.map((task) => <article key={task.id} className="border border-[#202020] bg-[#0A0A0A] p-5"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start"><div><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">{task.id} · {task.priority}</p><h2 className="mt-2 text-lg text-white">{task.title}</h2><p className="mt-2 text-sm text-[#777772]">{task.description}</p></div><span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#C8C8C3]">{task.status}</span></div><div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#202020] pt-4"><span className="text-xs text-[#777772]">Agent: {agents.find((agent) => agent.id === task.agentId)?.name || "Unassigned"}</span><div className="flex gap-2">{task.status === "COMPLETED" ? <button type="button" onClick={() => runTask(task.id)} className="inline-flex items-center gap-2 border border-[#2A2A2A] px-3 py-2 text-xs text-[#D8D8D8] hover:border-white"><RotateCcw size={14} /> Retry</button> : task.status === "RUNNING" ? <button type="button" disabled className="border border-[#2A2A2A] px-3 py-2 text-xs text-[#777772]">RUNNING...</button> : <button type="button" onClick={() => runTask(task.id)} className="inline-flex items-center gap-2 border border-white bg-white px-3 py-2 text-xs text-black"><Play size={14} /> Run</button>}{!["COMPLETED", "CANCELLED"].includes(task.status) && <button type="button" onClick={() => cancelTask(task.id)} className="inline-flex items-center gap-2 border border-[#2A2A2A] px-3 py-2 text-xs text-[#D8D8D8] hover:border-white"><Ban size={14} /> Cancel</button>}</div></div>{task.result && <p className="mt-4 border-l border-white pl-3 text-sm text-[#C8C8C3]">{task.result}</p>}</article>)}</div>
  </div>;
}
