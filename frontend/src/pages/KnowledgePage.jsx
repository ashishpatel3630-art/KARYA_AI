import { FilePlus2, Search } from "lucide-react";
import { useMemo, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function KnowledgePage() {
  const { knowledge, addKnowledge } = useOperations();
  const [query, setQuery] = useState("");
  const [name, setName] = useState("");
  const filtered = useMemo(() => knowledge.filter((item) => item.name.toLowerCase().includes(query.toLowerCase())), [knowledge, query]);
  function addDocument(event) { event.preventDefault(); if (!name.trim()) return; addKnowledge({ name: name.trim(), type: "DOCUMENT" }); setName(""); }
  return <div><PageHeader eyebrow="Memory" title="Knowledge" description="Indexed sources become context for agents and evidence for workflows." action={<form onSubmit={addDocument} className="flex gap-2"><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Document name" className="w-40 border border-[#2A2A2A] bg-[#0A0A0A] px-3 py-3 text-xs text-white outline-none focus:border-white sm:w-52" /><button className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black"><FilePlus2 size={15} /> Index</button></form>} />
    <div className="mb-5 flex items-center gap-3 border border-[#2A2A2A] bg-[#0A0A0A] px-4 py-3"><Search size={15} className="text-[#777772]" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search indexed sources" className="w-full bg-transparent text-sm text-white outline-none placeholder:text-[#555550]" /></div>
    <div className="space-y-3">{filtered.map((item) => <article key={item.id} className="flex flex-col justify-between gap-4 border border-[#202020] bg-[#0A0A0A] p-5 sm:flex-row sm:items-center"><div><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">{item.type} · {item.size}</p><h2 className="mt-2 text-lg text-white">{item.name}</h2><p className="mt-2 text-xs text-[#777772]">Used by {item.usedByAgents} agents and {item.usedByWorkflows} workflows</p></div><span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#C8C8C3]">{item.status}</span></article>)}</div>
  </div>;
}
