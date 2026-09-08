import { ArrowRight, Command, Search, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useOperations } from "../../context/OperationsContext";

const COMMANDS = [
  { label: "Go to Overview", meta: "Workspace", to: "/app" },
  { label: "Go to AI Employees", meta: "Workforce", to: "/app/agents" },
  { label: "Go to Tasks", meta: "Execution", to: "/app/tasks" },
  { label: "Go to Workflows", meta: "Automation", to: "/app/workflows" },
  { label: "Search Knowledge", meta: "Evidence", to: "/app/knowledge" },
  { label: "View Integrations", meta: "Tools", to: "/app/integrations" },
  { label: "View Activity", meta: "Audit trail", to: "/app/activity" },
  { label: "Review Approvals", meta: "Human control", to: "/app/approvals" },
  { label: "Open Analytics", meta: "System intelligence", to: "/app/analytics" },
  { label: "Open Settings", meta: "System", to: "/app/settings" },
];

export default function CommandPalette() {
  const navigate = useNavigate();
  const { agents, tasks, workflows, knowledge, integrations, activities, approvals } = useOperations();
  const inputRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const navigateTo = useCallback((path) => {
    setOpen(false);
    navigate(path);
  }, [navigate]);

  const filteredCommands = useMemo(() => {
    const entities = [
      ...agents.map((item) => ({ label: item.name, meta: "Agent", to: "/app/agents" })),
      ...tasks.map((item) => ({ label: item.title, meta: "Task", to: "/app/tasks" })),
      ...workflows.map((item) => ({ label: item.name, meta: "Workflow", to: "/app/workflows" })),
      ...knowledge.map((item) => ({ label: item.name, meta: "Knowledge", to: "/app/knowledge" })),
      ...integrations.map((item) => ({ label: item.name, meta: "Integration", to: "/app/integrations" })),
      ...activities.map((item) => ({ label: item.description, meta: "Activity", to: "/app/activity" })),
      ...approvals.map((item) => ({ label: item.action, meta: "Approval", to: "/app/approvals" })),
    ];
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return COMMANDS;

    return [...COMMANDS, ...entities].filter((command) =>
      `${command.label} ${command.meta}`.toLowerCase().includes(normalizedQuery),
    );
  }, [query, agents, tasks, workflows, knowledge, integrations, activities, approvals]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen(true);
        return;
      }

      if (!open) return;

      if (event.key === "Escape") {
        setOpen(false);
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((index) =>
          filteredCommands.length ? (index + 1) % filteredCommands.length : 0,
        );
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((index) =>
          filteredCommands.length
            ? (index - 1 + filteredCommands.length) % filteredCommands.length
            : 0,
        );
      }

      if (event.key === "Enter" && filteredCommands[activeIndex]) {
        event.preventDefault();
        navigateTo(filteredCommands[activeIndex].to);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeIndex, filteredCommands, navigateTo, open]);

  useEffect(() => {
    if (open) {
      window.setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  function openPalette() {
    setQuery("");
    setActiveIndex(0);
    setOpen(true);
  }

  return (
    <>
      <button
        type="button"
        onClick={openPalette}
        className="hidden items-center gap-3 border border-[#242424] bg-[#0A0A0A] px-3 py-2 text-[#777772] transition hover:border-[#555550] hover:text-white sm:flex"
        aria-label="Open KARYA command palette"
      >
        <Search size={14} />
        <span className="text-[10px] uppercase tracking-[0.18em]">Search KARYA</span>
        <kbd className="border border-[#2A2A2A] px-1.5 py-0.5 font-mono text-[9px] text-[#555550]">⌘K</kbd>
      </button>

      {open && (
        <div className="fixed inset-0 z-[200] flex items-start justify-center bg-black/80 px-4 pt-[12vh] backdrop-blur-sm" onMouseDown={() => setOpen(false)}>
          <section
            role="dialog"
            aria-modal="true"
            aria-label="KARYA command palette"
            className="w-full max-w-xl overflow-hidden border border-[#383838] bg-[#0A0A0A] shadow-2xl"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="flex items-center gap-3 border-b border-[#242424] px-4 py-4">
              <Command size={16} className="text-[#777772]" />
              <input
                ref={inputRef}
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setActiveIndex(0);
                }}
                placeholder="Search KARYA"
                className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-[#555550]"
              />
              <button type="button" onClick={() => setOpen(false)} aria-label="Close command palette" className="text-[#777772] hover:text-white">
                <X size={16} />
              </button>
            </div>

            <div className="max-h-[55vh] overflow-y-auto p-2">
              {filteredCommands.length ? (
                filteredCommands.map((command, index) => (
                  <button
                    key={command.to}
                    type="button"
                    onClick={() => navigateTo(command.to)}
                    className={`flex w-full items-center justify-between px-3 py-3 text-left transition ${index === activeIndex ? "bg-white text-black" : "text-[#D8D8D8] hover:bg-[#151515]"}`}
                  >
                    <span>
                      <span className="block text-sm">{command.label}</span>
                      <span className={`mt-1 block font-mono text-[9px] uppercase tracking-[0.16em] ${index === activeIndex ? "text-black/60" : "text-[#666661]"}`}>{command.meta}</span>
                    </span>
                    <ArrowRight size={15} />
                  </button>
                ))
              ) : (
                <p className="px-3 py-8 text-center text-sm text-[#777772]">No KARYA command matches that search.</p>
              )}
            </div>

            <div className="flex items-center justify-between border-t border-[#242424] px-4 py-3 font-mono text-[9px] uppercase tracking-[0.16em] text-[#555550]">
              <span>Navigate with arrows</span>
              <span>Esc to close</span>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
