import React, { useEffect, useMemo, useRef, useState } from "react";

const NODES = [
  {
    label: "LOCAL INFERENCE",
    angle: -90,
    distance: 178,
  },
  {
    label: "KNOWLEDGE",
    angle: -42,
    distance: 184,
  },
  {
    label: "TOOLS",
    angle: 4,
    distance: 178,
  },
  {
    label: "EVIDENCE",
    angle: 58,
    distance: 182,
  },
  {
    label: "AGENT CORE",
    angle: 120,
    distance: 180,
  },
  {
    label: "DOCUMENTS",
    angle: 174,
    distance: 180,
  },
  {
    label: "RAG",
    angle: 224,
    distance: 175,
  },
  {
    label: "MCP",
    angle: 284,
    distance: 180,
  },
];

const ease = (value) =>
  1 - Math.pow(1 - value, 3.2);

export default function Hero() {
  const coreRef = useRef(null);

  const [ready, setReady] = useState(false);
  const [pointer, setPointer] = useState({
    x: 0,
    y: 0,
  });

  const [hovered, setHovered] = useState(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setReady(true);
    }, 120);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleMove = (event) => {
      if (!coreRef.current) return;

      const rect =
        coreRef.current.getBoundingClientRect();

      const x =
        (event.clientX -
          (rect.left + rect.width / 2)) /
        (rect.width / 2);

      const y =
        (event.clientY -
          (rect.top + rect.height / 2)) /
        (rect.height / 2);

      setPointer({
        x: Math.max(-1, Math.min(1, x)),
        y: Math.max(-1, Math.min(1, y)),
      });
    };

    const reset = () => {
      setPointer({
        x: 0,
        y: 0,
      });
    };

    window.addEventListener("pointermove", handleMove, {
      passive: true,
    });

    window.addEventListener("pointerleave", reset);

    return () => {
      window.removeEventListener(
        "pointermove",
        handleMove
      );

      window.removeEventListener(
        "pointerleave",
        reset
      );
    };
  }, []);

  const nodes = useMemo(() => {
    return NODES.map((node, index) => {
      const radians =
        (node.angle * Math.PI) / 180;

      return {
        ...node,
        id: index,
        x:
          Math.cos(radians) * node.distance,
        y:
          Math.sin(radians) * node.distance,
      };
    });
  }, []);

  const tx = pointer.x * 5;
  const ty = pointer.y * 5;

  return (
    <section
      id="home"
      className="
        relative
        min-h-screen
        overflow-hidden
        bg-[#050505]
        text-white
      "
    >
      {/* BACKGROUND CROSSHAIR */}

      <div
        className="
          pointer-events-none
          absolute
          inset-0
          opacity-[0.35]
        "
      >
        <div className="absolute left-1/2 top-0 h-full w-px bg-[#111111]" />

        <div className="absolute left-0 top-1/2 h-px w-full bg-[#111111]" />
      </div>

      {/* AMBIENT CORNERS */}

      <div className="pointer-events-none absolute left-0 top-0 h-40 w-40 border-l border-t border-[#181818]" />

      <div className="pointer-events-none absolute bottom-0 right-0 h-40 w-40 border-b border-r border-[#181818]" />

      {/* HERO */}

      <div className="relative z-10 mx-auto flex min-h-screen max-w-[1500px] items-center px-6 pb-16 pt-28 sm:px-10 lg:px-14">
        <div className="grid w-full grid-cols-1 items-center gap-16 lg:grid-cols-[0.9fr_1.1fr] lg:gap-4">
          {/* LEFT */}

          <div
            className={`
              relative
              z-20
              max-w-[760px]
              transition-all
              duration-[1400ms]
              ease-[cubic-bezier(0.16,1,0.3,1)]
              ${
                ready
                  ? "translate-y-0 opacity-100"
                  : "translate-y-10 opacity-0"
              }
            `}
          >
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.3em] text-[#777772]">
                SOVEREIGN AI WORKBENCH
              </span>

              <span className="font-mono text-[8px] text-[#3A3A36]">
                / 01
              </span>
            </div>

            <h1 className="text-[clamp(3.3rem,6.6vw,7.2rem)] font-semibold uppercase leading-[0.86] tracking-[-0.07em]">
              <span className="block">
                THE SOVEREIGN AI
              </span>

              <span className="block">
                WORKFORCE FOR
              </span>

              <span className="block text-[#9A9A95]">
                INDUSTRIAL WORK.
              </span>
            </h1>

            <div
              className={`
                transition-all
                delay-300
                duration-1000
                ${
                  ready
                    ? "translate-y-0 opacity-100"
                    : "translate-y-5 opacity-0"
                }
              `}
            >
              <p className="mt-8 max-w-[570px] text-[15px] leading-7 text-[#858580] sm:text-[16px]">
                KARYA brings local intelligence, agentic
                execution, and source-grounded reasoning
                to confidential industrial environments.
              </p>
            </div>

            <div
              className={`
                mt-9
                flex
                flex-col
                gap-3
                transition-all
                delay-500
                duration-1000
                sm:flex-row
                ${
                  ready
                    ? "translate-y-0 opacity-100"
                    : "translate-y-5 opacity-0"
                }
              `}
            >
              <a
                href="/app"
                className="
                  group
                  flex
                  h-12
                  items-center
                  justify-center
                  gap-4
                  bg-white
                  px-7
                  font-mono
                  text-[9px]
                  font-semibold
                  tracking-[0.2em]
                  text-black
                  transition-all
                  duration-500
                  hover:bg-[#DCDCDC]
                "
              >
                ENTER KARYA

                <span className="transition-transform duration-500 group-hover:translate-x-1">
                  →
                </span>
              </a>

              <button
                type="button"
                onClick={() =>
                  document
                    .getElementById("product")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    })
                }
                className="
                  flex
                  h-12
                  items-center
                  justify-center
                  border
                  border-[#333333]
                  px-7
                  font-mono
                  text-[9px]
                  font-semibold
                  tracking-[0.2em]
                  text-[#B5B5B0]
                  transition-all
                  duration-500
                  hover:border-[#777777]
                  hover:text-white
                "
              >
                EXPLORE PLATFORM
              </button>
            </div>

            <div className="mt-12 flex flex-wrap gap-x-4 gap-y-3 border-t border-[#1B1B1B] pt-5">
              {[
                "LOCAL INFERENCE",
                "PRIVATE KNOWLEDGE",
                "AGENTIC EXECUTION",
                "AUDITABLE",
              ].map((item, index) => (
                <React.Fragment key={item}>
                  <span className="font-mono text-[7px] tracking-[0.18em] text-[#575752]">
                    {item}
                  </span>

                  {index !== 3 && (
                    <span className="hidden text-[#292925] sm:inline">
                      /
                    </span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* CORE */}

          <div
            ref={coreRef}
            className={`
              relative
              mx-auto
              flex
              aspect-square
              w-full
              max-w-[650px]
              items-center
              justify-center
              transition-all
              delay-200
              duration-[1800ms]
              ease-[cubic-bezier(0.16,1,0.3,1)]
              ${
                ready
                  ? "translate-x-0 scale-100 opacity-100"
                  : "translate-x-10 scale-[0.94] opacity-0"
              }
            `}
          >
            <div
              className="
                absolute
                inset-0
                transition-transform
                duration-700
                ease-out
              "
              style={{
                transform: `translate3d(${tx}px, ${ty}px, 0)`,
              }}
            >
              {/* OUTER RING */}

              <div className="absolute left-1/2 top-1/2 aspect-square w-[82%] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#1D1D1D]" />

              {/* ORBIT */}

              <div className="absolute left-1/2 top-1/2 aspect-square w-[72%] -translate-x-1/2 -translate-y-1/2 animate-[spin_48s_linear_infinite] rounded-full border border-dashed border-[#363636]" />

              {/* INNER */}

              <div className="absolute left-1/2 top-1/2 aspect-square w-[56%] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#292929]" />

              <div className="absolute left-1/2 top-1/2 aspect-square w-[38%] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#1D1D1D]" />

              {/* SVG */}

              <svg
                viewBox="0 0 600 600"
                className="absolute inset-0 h-full w-full overflow-visible"
                aria-hidden="true"
              >
                <line
                  x1="300"
                  y1="50"
                  x2="300"
                  y2="550"
                  stroke="#181818"
                  strokeWidth="1"
                  strokeDasharray="2 10"
                />

                <line
                  x1="50"
                  y1="300"
                  x2="550"
                  y2="300"
                  stroke="#181818"
                  strokeWidth="1"
                  strokeDasharray="2 10"
                />

                {nodes.map((node) => {
                  const x = 300 + node.x;
                  const y = 300 + node.y;

                  return (
                    <g key={node.id}>
                      <line
                        x1="300"
                        y1="300"
                        x2={x}
                        y2={y}
                        stroke={
                          hovered === node.id
                            ? "#777777"
                            : "#292929"
                        }
                        strokeWidth={
                          hovered === node.id
                            ? "1.2"
                            : "0.7"
                        }
                        strokeDasharray={
                          hovered === node.id
                            ? "none"
                            : "3 7"
                        }
                      />

                      <circle
                        cx={x}
                        cy={y}
                        r={
                          hovered === node.id
                            ? "6"
                            : "4"
                        }
                        fill="#050505"
                        stroke={
                          hovered === node.id
                            ? "#FFFFFF"
                            : "#656560"
                        }
                        strokeWidth="1"
                      />

                      <circle
                        cx={x}
                        cy={y}
                        r="1.5"
                        fill="#FFFFFF"
                      />
                    </g>
                  );
                })}

                <polygon
                  points="300,190 410,300 300,410 190,300"
                  fill="none"
                  stroke="#60605B"
                  strokeWidth="0.8"
                />

                <polygon
                  points="300,235 365,300 300,365 235,300"
                  fill="none"
                  stroke="#353532"
                  strokeWidth="0.8"
                />

                <line
                  x1="300"
                  y1="190"
                  x2="300"
                  y2="300"
                  stroke="#666662"
                  strokeWidth="0.8"
                />

                <line
                  x1="410"
                  y1="300"
                  x2="300"
                  y2="300"
                  stroke="#666662"
                  strokeWidth="0.8"
                />

                <line
                  x1="300"
                  y1="410"
                  x2="300"
                  y2="300"
                  stroke="#666662"
                  strokeWidth="0.8"
                />

                <line
                  x1="190"
                  y1="300"
                  x2="300"
                  y2="300"
                  stroke="#666662"
                  strokeWidth="0.8"
                />
              </svg>

              {/* LABELS */}

              {nodes.map((node) => {
                const left =
                  50 + (node.x / 330) * 50;

                const top =
                  50 + (node.y / 330) * 50;

                return (
                  <button
                    key={node.id}
                    type="button"
                    onMouseEnter={() =>
                      setHovered(node.id)
                    }
                    onMouseLeave={() =>
                      setHovered(null)
                    }
                    className="
                      absolute
                      z-20
                      -translate-x-1/2
                      -translate-y-1/2
                      whitespace-nowrap
                      font-mono
                      text-[6px]
                      tracking-[0.15em]
                      text-[#575752]
                      transition-all
                      duration-500
                      hover:text-white
                      sm:text-[7px]
                    "
                    style={{
                      left: `${left}%`,
                      top: `${top}%`,
                    }}
                  >
                    {node.label}
                  </button>
                );
              })}

              {/* CORE */}

              <div className="absolute left-1/2 top-1/2 flex h-[110px] w-[110px] -translate-x-1/2 -translate-y-1/2 items-center justify-center">
                <div className="absolute inset-0 rotate-45 border border-[#70706B]" />

                <div className="absolute inset-[14px] rotate-45 border border-[#292929]" />

                <span className="relative z-10 font-sans text-[52px] font-semibold tracking-[-0.1em] text-white">
                  K
                </span>

                <span className="absolute bottom-3 right-3 h-1.5 w-1.5 rounded-full bg-white" />
              </div>
            </div>

            <div className="absolute bottom-[4%] left-1/2 -translate-x-1/2 text-center">
              <p className="whitespace-nowrap font-mono text-[7px] font-semibold tracking-[0.28em] text-white sm:text-[8px]">
                KARYA INTELLIGENCE CORE
              </p>

              <p className="mt-2 whitespace-nowrap font-mono text-[6px] tracking-[0.2em] text-[#4D4D49]">
                LOCAL · PRIVATE · SOURCE-GROUNDED
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 border-t border-[#171717]">
        <div className="mx-auto flex max-w-[1500px] justify-between px-6 py-3 sm:px-10 lg:px-14">
          <span className="font-mono text-[7px] tracking-[0.2em] text-[#464641]">
            SOVEREIGN ARCHITECTURE
          </span>

          <span className="font-mono text-[7px] tracking-[0.2em] text-[#464641]">
            KRY // SYS
          </span>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from {
            transform: translate(-50%, -50%) rotate(0deg);
          }

          to {
            transform: translate(-50%, -50%) rotate(360deg);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </section>
  );
}