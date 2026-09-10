import {
  ChevronDown,
  FileText,
  Send,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";

import PageHeader from "../components/common/PageHeader";
import { useOperations } from "../context/OperationsContext";
import { askChat } from "../services/operations";


function SourceCard({ source, index }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="border border-[#202020] bg-[#0D0D0D]">
      <div className="flex items-center justify-between gap-4 p-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center border border-[#292929] bg-[#111111]">
            <FileText
              size={15}
              className="text-[#A8A8A3]"
            />
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm text-[#E8E8E3]">
              {source.document_name}
            </p>

            <p className="mt-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[#666661]">
              Page {source.page || "Unknown"}
            </p>
          </div>
        </div>

        <span className="shrink-0 font-mono text-[9px] uppercase tracking-[0.14em] text-[#777772]">
          [{index + 1}]
        </span>
      </div>

      <div className="border-t border-[#202020]">
        <button
          type="button"
          onClick={() => setShowDetails((value) => !value)}
          className="flex w-full items-center justify-between px-4 py-3 text-left transition hover:bg-[#111111]"
        >
          <span className="font-mono text-[9px] uppercase tracking-[0.15em] text-[#666661]">
            Evidence details
          </span>

          <ChevronDown
            size={14}
            className={`text-[#666661] transition-transform ${
              showDetails ? "rotate-180" : ""
            }`}
          />
        </button>

        {showDetails && (
          <div className="border-t border-[#202020] px-4 py-4">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#555550]">
                  Page
                </p>

                <p className="mt-1 text-[#B8B8B3]">
                  {source.page || "Unknown"}
                </p>
              </div>

              <div>
                <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#555550]">
                  Chunk
                </p>

                <p className="mt-1 text-[#B8B8B3]">
                  {source.chunk_id}
                </p>
              </div>

              <div>
                <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#555550]">
                  Retrieval score
                </p>

                <p className="mt-1 text-[#B8B8B3]">
                  {typeof source.score === "number"
                    ? source.score.toFixed(3)
                    : "—"}
                </p>
              </div>

              <div>
                <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#555550]">
                  Evidence
                </p>

                <p className="mt-1 text-[#B8B8B3]">
                  Verified
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


export default function ChatPage() {
  const { knowledge } = useOperations();

  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();

    const question = message.trim();

    if (!question) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer(null);

    try {
      const readyDocumentIds = knowledge
        .filter(
          (document) =>
            document.status === "READY"
        )
        .map(
          (document) =>
            document.id
        );

      const response = await askChat(
        question,
        readyDocumentIds
      );

      setAnswer({
        answer:
          typeof response.answer === "string"
            ? response.answer.trim()
            : "No answer was returned.",

        sources: Array.isArray(
          response.sources
        )
          ? response.sources
          : [],
      });

      setMessage("");
    } catch (requestError) {
      setError(
        requestError?.message ||
          "Unable to process the question."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Workspace"
        title="Ask KARYA"
        description="Questions are answered from your ready knowledge sources through the local RAG and LLM services."
      />

      {/* -------------------------------------------------------
          QUESTION INPUT
      ------------------------------------------------------- */}

      <form
        onSubmit={submit}
        className="border border-[#202020] bg-[#0A0A0A] p-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <div className="h-1.5 w-1.5 bg-white" />

          <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#666661]">
            Local knowledge query
          </span>
        </div>

        <textarea
          value={message}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          placeholder="Ask a question about your uploaded documents"
          rows={4}
          disabled={loading}
          className="w-full resize-y bg-transparent text-sm leading-6 text-white outline-none placeholder:text-[#555550] disabled:opacity-50"
        />

        <div className="mt-4 flex items-center justify-between border-t border-[#202020] pt-4">
          <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-[#555550]">
            {knowledge.filter(
              (document) =>
                document.status === "READY"
            ).length}{" "}
            knowledge sources ready
          </span>

          <button
            type="submit"
            disabled={
              loading ||
              !message.trim()
            }
            className="inline-flex items-center gap-2 border border-white bg-white px-4 py-3 text-xs uppercase tracking-[0.16em] text-black transition hover:bg-[#DCDCD7] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Send size={14} />

            {loading
              ? "Retrieving"
              : "Ask KARYA"}
          </button>
        </div>
      </form>

      {/* -------------------------------------------------------
          ERROR
      ------------------------------------------------------- */}

      {error && (
        <div className="mt-4 border border-[#5A2A2A] bg-[#1A0A0A] p-4">
          <p className="font-mono text-[9px] uppercase tracking-[0.15em] text-[#B56F6F]">
            Query failed
          </p>

          <p className="mt-2 text-sm leading-6 text-[#F0B0B0]">
            {error}
          </p>
        </div>
      )}

      {/* -------------------------------------------------------
          ANSWER
      ------------------------------------------------------- */}

      {answer && (
        <section className="mt-8">
          {/* Answer card */}

          <div className="border border-[#202020] bg-[#0A0A0A] p-6">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center border border-[#292929] bg-[#111111]">
                  <ShieldCheck
                    size={15}
                    className="text-[#BDBDB8]"
                  />
                </div>

                <div>
                  <h2 className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">
                    Answer
                  </h2>

                  <p className="mt-1 font-mono text-[8px] uppercase tracking-[0.14em] text-[#4F4F4A]">
                    Grounded response
                  </p>
                </div>
              </div>

              {answer.sources.length > 0 && (
                <span className="font-mono text-[8px] uppercase tracking-[0.15em] text-[#777772]">
                  Verified
                </span>
              )}
            </div>

            <div className="mt-6 border-l border-white pl-4">
              <p className="whitespace-pre-wrap text-base leading-8 text-[#F5F5F5]">
                {answer.answer}
              </p>
            </div>
          </div>

          {/* ---------------------------------------------------
              SOURCES
          --------------------------------------------------- */}

          <div className="mt-4 border border-[#202020] bg-[#0A0A0A] p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">
                  Verified sources
                </h2>

                <p className="mt-2 text-xs text-[#555550]">
                  Evidence used to ground this response.
                </p>
              </div>

              <span className="font-mono text-[9px] uppercase tracking-[0.15em] text-[#777772]">
                {answer.sources.length}
              </span>
            </div>

            {answer.sources.length > 0 ? (
              <div className="mt-5 space-y-3">
                {answer.sources.map(
                  (source, index) => (
                    <SourceCard
                      key={`${source.document_name}-${source.page}-${source.chunk_id}`}
                      source={source}
                      index={index}
                    />
                  )
                )}
              </div>
            ) : (
              <div className="mt-5 border border-[#202020] bg-[#0D0D0D] p-4">
                <p className="text-sm text-[#666661]">
                  No relevant sources were retrieved.
                </p>
              </div>
            )}
          </div>
        </section>
      )}

      {/* -------------------------------------------------------
          EMPTY STATE
      ------------------------------------------------------- */}

      {!answer && !loading && !error && (
        <div className="mt-8 border border-dashed border-[#202020] bg-[#080808] p-10 text-center">
          <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#555550]">
            Ready for local knowledge query
          </p>

          <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-[#444440]">
            Ask KARYA about information contained in your
            ready industrial documents.
          </p>
        </div>
      )}

      {/* -------------------------------------------------------
          RETRIEVING STATE
      ------------------------------------------------------- */}

      {loading && (
        <div className="mt-8 border border-[#202020] bg-[#0A0A0A] p-6">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 animate-pulse bg-white" />

            <div>
              <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#777772]">
                KARYA is retrieving evidence
              </p>

              <p className="mt-2 text-xs text-[#555550]">
                Searching local embeddings and generating a
                grounded response.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}