import { Send } from "lucide-react";
import { useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { askChat } from "../services/operations";
import { useOperations } from "../context/OperationsContext";

export default function ChatPage() {
  const { knowledge } = useOperations();
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await askChat(message.trim(), knowledge.filter((document) => document.status === "READY").map((document) => document.id));
      setAnswer(response);
      setMessage("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return <div><PageHeader eyebrow="Workspace" title="Ask KARYA" description="Questions are answered from your ready knowledge sources through the existing RAG and LLM services." />
    <form onSubmit={submit} className="border border-[#202020] bg-[#0A0A0A] p-5"><textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask a question about your uploaded documents" rows={4} className="w-full resize-y bg-transparent text-sm text-white outline-none placeholder:text-[#555550]" /><div className="mt-4 flex justify-end"><button disabled={loading || !message.trim()} className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black disabled:opacity-50"><Send size={14} /> {loading ? "Retrieving" : "Ask"}</button></div></form>
    {error && <p className="mt-4 border border-[#5A2A2A] bg-[#1A0A0A] p-4 text-sm text-[#F0B0B0]">{error}</p>}
    {answer && <section className="mt-8 border border-[#202020] bg-[#0A0A0A] p-6"><h2 className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">Answer</h2><p className="mt-4 whitespace-pre-wrap text-base leading-7 text-[#F5F5F5]">{answer.answer}</p><h2 className="mt-8 border-t border-[#202020] pt-5 font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">Sources</h2>{answer.sources.length ? <div className="mt-4 space-y-3">{answer.sources.map((source) => <div key={`${source.document_id}-${source.chunk_id}`} className="border-l border-white pl-3 text-sm text-[#C8C8C3]">{source.document_name} · Page {source.page || "Unknown"} · Chunk {source.chunk_id} · {source.score.toFixed(3)}</div>)}</div> : <p className="mt-4 text-sm text-[#777772]">No relevant sources were retrieved.</p>}</section>}
  </div>;
}