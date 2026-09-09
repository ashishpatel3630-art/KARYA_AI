import { FilePlus2, Search } from "lucide-react";
import { useMemo, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";

export default function KnowledgePage() {
  const { knowledge, addKnowledge } = useOperations();
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const filtered = useMemo(() => knowledge.filter((item) => item.name.toLowerCase().includes(query.toLowerCase())), [knowledge, query]);
  function addDocument(event) { event.preventDefault(); if (file) addKnowledge(file); setFile(null); event.target.reset(); }
  return <div><PageHeader eyebrow="Memory" title="Knowledge" description="Uploaded sources are processed by the existing document and RAG pipeline." action={<form onSubmit={addDocument} className="flex gap-2"><input type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} accept=".pdf,.docx,.xlsx,.pptx" className="w-44 border border-[#2A2A2A] bg-[#0A0A0A] px-3 py-3 text-xs text-white sm:w-56" /><button disabled={!file} className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black disabled:cursor-not-allowed disabled:opacity-50"><FilePlus2 size={15} /> Upload</button></form>} />
    <div className="mb-5 flex items-center gap-3 border border-[#2A2A2A] bg-[#0A0A0A] px-4 py-3"><Search size={15} className="text-[#777772]" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search indexed sources" className="w-full bg-transparent text-sm text-white outline-none placeholder:text-[#555550]" /></div>
    <div className="space-y-3">{filtered.map((item) => <article key={item.id} className="flex flex-col justify-between gap-4 border border-[#202020] bg-[#0A0A0A] p-5 sm:flex-row sm:items-center"><div><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">{item.type} · {item.size}</p><h2 className="mt-2 text-lg text-white">{item.name}</h2><p className="mt-2 text-xs text-[#777772]">Used by {item.usedByAgents} agents and {item.usedByWorkflows} workflows</p></div><span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#C8C8C3]">{item.status}</span></article>)}</div>
  </div>;
}
