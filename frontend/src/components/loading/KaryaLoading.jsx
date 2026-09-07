import React, { useEffect, useMemo, useState } from "react";

const MODULES = [
  { name: "LOCAL INFERENCE", code: "LCL_INF" },
  { name: "SECURE RUNTIME", code: "SEC_RT" },
  { name: "KNOWLEDGE ENGINE", code: "KB_ENG" },
  { name: "AGENT CORE", code: "AGT_CR" },
];

const easeOut = (value) => 1 - Math.pow(1 - value, 3.2);

export default function KaryaLoading({
  duration = 5200,
  onComplete,
}) {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState("assembling");
  const [isDone, setIsDone] = useState(false);

  const fragments = useMemo(
    () => [
      { id: 1, startX: -190, startY: -105, targetX: -48, targetY: -48, type: "node", size: 2, delay: 0.02 },
      { id: 2, startX: 200, startY: -130, targetX: 52, targetY: -52, type: "line", width: 38, angle: -28, delay: 0.07 },
      { id: 3, startX: -240, startY: 35, targetX: -65, targetY: 12, type: "node", size: 1.6, delay: 0.10 },
      { id: 4, startX: 170, startY: 160, targetX: 45, targetY: 52, type: "node", size: 2.2, delay: 0.05 },
      { id: 5, startX: 0, startY: -200, targetX: 0, targetY: -62, type: "line", width: 26, angle: 90, delay: 0.14 },
      { id: 6, startX: -160, startY: 170, targetX: -38, targetY: 55, type: "node", size: 1.8, delay: 0.03 },
      { id: 7, startX: 220, startY: -20, targetX: 68, targetY: 6, type: "node", size: 1.6, delay: 0.11 },
      { id: 8, startX: -110, startY: -170, targetX: -30, targetY: -48, type: "line", width: 32, angle: 45, delay: 0.09 },
      { id: 9, startX: 130, startY: 190, targetX: 32, targetY: 62, type: "line", width: 42, angle: -18, delay: 0.06 },
      { id: 10, startX: -190, startY: -15, targetX: -62, targetY: 0, type: "line", width: 30, angle: 0, delay: 0.12 },
      { id: 11, startX: 150, startY: 75, targetX: 55, targetY: 28, type: "node", size: 1.8, delay: 0.08 },
      { id: 12, startX: -50, startY: 200, targetX: -12, targetY: 68, type: "line", width: 24, angle: 90, delay: 0.15 },
    ],
    []
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mediaQuery.matches) {
      setProgress(100);
      setPhase("ready");
      setIsDone(true);
      onComplete?.();
      return;
    }

    const startTime = performance.now();
    let frameId;
    let completionTimer;

    const animate = (now) => {
      const elapsed = now - startTime;
      const raw = Math.min(elapsed / duration, 1);
      const eased = easeOut(raw);

      setProgress(eased * 100);

      if (raw < 0.5) {
        setPhase("assembling");
      } else if (raw < 0.82) {
        setPhase("synchronizing");
      } else if (raw < 0.94) {
        setPhase("collapsing");
      } else if (raw < 1) {
        setPhase("ready");
      } else {
        setPhase("exiting");
        completionTimer = window.setTimeout(() => {
          setIsDone(true);
          onComplete?.();
        }, 650);
        return;
      }

      frameId = requestAnimationFrame(animate);
    };

    frameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frameId);
      if (completionTimer) clearTimeout(completionTimer);
    };
  }, [duration, onComplete]);

  if (isDone) return null;

  const t = progress / 100;
  const collapseProgress = phase === "collapsing" || phase === "ready" ? Math.min(1, Math.max(0, (t - 0.82) / 0.18)) : 0;
  const synchronizationProgress = phase === "synchronizing" ? Math.min(1, Math.max(0, (t - 0.5) / 0.32)) : phase === "collapsing" || phase === "ready" ? 1 : 0;
  const coreScale = 1 - collapseProgress * 0.72;

  // Left-to-center entrance math for the title and primary layout block
  const entranceProgress = easeOut(Math.min(1, t / 0.35));
  const translateXOffset = (1 - entranceProgress) * -42;
  const opacityEntrance = Math.min(1, t * 3);

  const systemStatus =
    phase === "assembling"
      ? "INITIALIZING VECTOR TOPOLOGY"
      : phase === "synchronizing"
      ? "SYNCHRONIZING RUNTIME NODES"
      : phase === "collapsing"
      ? "FINALIZING SYSTEM HANDSHAKE"
      : "SYSTEM READY";

  return (
    <div
      className={`
        fixed inset-0 z-[99999] flex flex-col items-center justify-between
        overflow-hidden bg-[#FAFAFA] px-6 py-6 text-[#111111] select-none
        transition-all duration-[700ms] ease-[cubic-bezier(0.16,1,0.3,1)]
        sm:px-10 sm:py-8 md:px-14 md:py-10
        ${phase === "exiting" ? "scale-[1.015] opacity-0 blur-[2px]" : "scale-100 opacity-100"}
      `}
    >
      {/* =====================================================
          SUBTLE ARCHITECTURAL GRID BACKGROUND
      ===================================================== */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute inset-0 bg-[radial-gradient(#E2E2E2_1px,transparent_1px)] [background-size:24px_24px]" />
        <div className="absolute left-1/2 top-1/2 h-[1px] w-[85vw] max-w-[900px] -translate-x-1/2 bg-[#E5E5E5]" />
        <div className="absolute left-1/2 top-1/2 h-[85vh] w-[1px] max-h-[900px] -translate-y-1/2 bg-[#E5E5E5]" />
      </div>

      {/* =====================================================
          TOP SYSTEM BAR
      ===================================================== */}
      <header className="relative z-25 flex w-full max-w-5xl items-center justify-between border-b border-[#E5E5E5] pb-3.5 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <span className={`h-2 w-2 rounded-full bg-[#111111] transition-all duration-500 ${phase === "ready" ? "scale-125 shadow-[0_0_10px_rgba(0,0,0,0.2)] animate-pulse" : "scale-100"}`} />
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.3em] text-[#111111]">
            KARYA OS
          </span>
          <span className="hidden font-mono text-[10px] tracking-[0.2em] text-[#A0A0A0] sm:inline">/</span>
          <span className="hidden font-mono text-[9px] tracking-[0.2em] text-[#666666] sm:inline font-medium">
            KERNEL v2.4.0-STABLE
          </span>
        </div>

        <div className="flex items-center gap-6 font-mono text-[9px] uppercase tracking-[0.22em] text-[#666666]">
          <span className="hidden sm:inline bg-[#F0F0F0] px-2.5 py-1 rounded border border-[#E0E0E0]">
            LOCAL ENCLAVE
          </span>
          <span className="text-[#111111] font-semibold">NODE_01</span>
        </div>
      </header>

      {/* =====================================================
          MAIN COMPOSITION (WITH LEFT-TO-CENTER ENTRANCE)
      ===================================================== */}
      <main
        className="relative z-10 my-auto flex w-full max-w-xl flex-col items-center justify-center py-4"
        style={{
          transform: `translateX(${translateXOffset}px)`,
          opacity: opacityEntrance,
        }}
      >
        
        {/* ================= CORE SYSTEM VISUAL ================= */}
        <div className="relative flex h-[220px] w-[220px] items-center justify-center">
          
          {/* Outer Ring */}
          <div
            className={`
              absolute h-[200px] w-[200px] rounded-full border border-[#DCDCDC]
              transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]
              ${phase === "assembling" ? "scale-[0.8] opacity-25" : "scale-100 opacity-80"}
              ${phase === "collapsing" ? "scale-[0.3] opacity-10" : ""}
            `}
          />

          {/* Rotating Data Orbit */}
          <div
            className={`
              absolute h-[155px] w-[155px] rounded-full border border-dashed border-[#CCCCCC]
              transition-all duration-700
            `}
            style={{
              transform: `rotate(${synchronizationProgress * 180}deg) scale(${
                phase === "collapsing" ? 0.25 : phase === "assembling" ? 0.7 : 1
              })`,
            }}
          />

          {/* SVG Geometry */}
          <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 220 220" aria-hidden="true">
            <line x1="110" y1="15" x2="110" y2="205" stroke="#D8D8D8" strokeWidth="0.5" strokeDasharray="1 4" opacity="0.8" />
            <line x1="15" y1="110" x2="205" y2="110" stroke="#D8D8D8" strokeWidth="0.5" strokeDasharray="1 4" opacity="0.8" />

            <g style={{ transform: `scale(${coreScale})`, transformOrigin: "110px 110px", transition: "transform 120ms linear" }}>
              <polygon
                points="110,60 160,110 110,160 60,110"
                fill="none"
                stroke="#111111"
                strokeWidth="1"
                strokeOpacity={0.75 * Math.min(1, t * 2)}
              />
              <circle cx="110" cy="110" r="18" fill="none" stroke="#666666" strokeWidth="0.75" strokeDasharray="2 2" />
            </g>

            {fragments.map((fragment) => {
              const localProgress = Math.min(1, Math.max(0, (t - fragment.delay) / (0.62 - fragment.delay)));
              const easedFragment = easeOut(localProgress);

              const currentX = 110 + fragment.startX + (fragment.targetX - fragment.startX) * easedFragment;
              const currentY = 110 + fragment.startY + (fragment.targetY - fragment.startY) * easedFragment;

              const finalX = currentX + (110 - currentX) * collapseProgress;
              const finalY = currentY + (110 - currentY) * collapseProgress;

              const fragmentOpacity = Math.min(1, localProgress * 2.2) * (1 - collapseProgress * 1.15);

              if (fragment.type === "node") {
                return <circle key={fragment.id} cx={finalX} cy={finalY} r={fragment.size} fill="#111111" opacity={fragmentOpacity} />;
              }

              return (
                <line
                  key={fragment.id}
                  x1={finalX}
                  y1={finalY}
                  x2={finalX + fragment.width * (1 - collapseProgress)}
                  y2={finalY}
                  stroke="#444444"
                  strokeWidth="0.8"
                  strokeOpacity={fragmentOpacity}
                  transform={`rotate(${fragment.angle}, ${finalX}, ${finalY})`}
                />
              );
            })}
          </svg>

          {/* Core Singularity Pulse */}
          <div
            className={`
              absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#111111]
              shadow-[0_0_20px_rgba(17,17,17,0.3)] transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]
              ${phase === "synchronizing" ? "scale-125" : ""}
              ${phase === "collapsing" ? "scale-[3]" : ""}
              ${phase === "ready" ? "scale-[2]" : ""}
            `}
          />
        </div>

        {/* ================= WORDMARK ================= */}
        <div className="mt-4 flex flex-col items-center">
          <h1 className="text-[42px] font-extrabold uppercase leading-none tracking-[-0.05em] text-[#111111] sm:text-[52px]">
            KARYA
          </h1>
          <div className="mt-2.5 flex items-center gap-3">
            <span className="h-px w-6 bg-[#CCCCCC]" />
            <p className="font-mono text-[8px] uppercase tracking-[0.4em] text-[#555555] sm:text-[9px] font-semibold">
              Autonomous Sovereign AI Workbench
            </p>
            <span className="h-px w-6 bg-[#CCCCCC]" />
          </div>
        </div>

        {/* ================= SYSTEM STATUS & PROGRESS ================= */}
        <section className="mt-7 w-full max-w-[420px] bg-white border border-[#E0E0E0] rounded-lg p-4 shadow-sm">
          <div className="mb-2.5 flex items-end justify-between">
            <div>
              <span className="font-mono text-[7px] uppercase tracking-[0.25em] text-[#888888] block">
                TELEMETRY STATUS
              </span>
              <span className="font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-[#111111]">
                {systemStatus}
              </span>
            </div>
            <span className="font-mono text-[11px] font-bold tracking-[0.1em] text-[#111111]">
              {String(Math.floor(progress)).padStart(3, "0")}%
            </span>
          </div>

          <div className="relative h-[3px] w-full overflow-hidden bg-[#EAEAEA] rounded-full">
            <div
              className="absolute inset-y-0 left-0 bg-[#111111] rounded-full transition-all duration-75 ease-linear"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* System Spec Ticker (Monochrome / Deterministic) */}
          <div className="mt-3 flex items-center justify-between border-t border-[#F0F0F0] pt-2">
            <span className="font-mono text-[7px] uppercase tracking-[0.2em] text-[#666666]">
              SYS_ALLOC: <strong className="text-[#111111] font-semibold">4096MB // L1_CACHE</strong>
            </span>
            <span className="font-mono text-[7px] uppercase tracking-[0.2em] text-[#444444] font-medium">
              [OK]
            </span>
          </div>
        </section>

        {/* ================= MODULE SYNCHRONIZATION GRID ================= */}
        <div className="mt-4 grid w-full max-w-[420px] grid-cols-2 gap-3">
          {MODULES.map((mod, index) => {
            const threshold = 0.4 + index * 0.1;
            const ready = t >= threshold + 0.08;
            const active = t >= threshold && !ready;

            return (
              <div
                key={mod.code}
                className={`
                  flex items-center justify-between p-2.5 rounded border transition-all duration-300
                  ${ready ? "bg-white border-[#CCCCCC] shadow-xs" : "bg-[#F7F7F7] border-[#E8E8E8] opacity-70"}
                `}
              >
                <div className="flex flex-col">
                  <span className="font-mono text-[7px] tracking-[0.15em] text-[#777777]">{mod.code}</span>
                  <span className={`font-mono text-[8px] font-bold tracking-[0.1em] ${ready ? "text-[#111111]" : "text-[#555555]"}`}>
                    {mod.name}
                  </span>
                </div>
                <span className={`font-mono text-[8px] font-semibold tracking-wider ${ready ? "text-[#111111]" : active ? "text-[#555555]" : "text-[#AAAAAA]"}`}>
                  {ready ? "[LOADED]" : active ? "[ACTIVE]" : "[QUEUED]"}
                </span>
              </div>
            );
          })}
        </div>
      </main>

      {/* =====================================================
          BOTTOM FOOTER BAR
      ===================================================== */}
      <footer className="relative z-20 flex w-full max-w-5xl items-center justify-between border-t border-[#E5E5E5] pt-3.5 text-[8px] font-mono tracking-[0.25em] text-[#666666]">
        <span>LOCAL ENCLAVE ACTIVE</span>
        <span className="hidden sm:inline text-[#444444] font-medium">LOCAL-FIRST RUNTIME ENVIRONMENT</span>
        <span>KRY // SYS</span>
      </footer>

      {/* =====================================================
          REDUCED MOTION OVERRIDE
      ===================================================== */}
      <style>{`
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}