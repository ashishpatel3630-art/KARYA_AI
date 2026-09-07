import React, { useEffect, useRef, useState } from "react";

const EVENTS = [
  ["PLANNER", "Requirement decomposed", "09:41:02"],
  ["REPOSITORY", "Architecture indexed", "09:41:08"],
  ["RESEARCH", "4 solutions generated", "09:41:19"],
  ["BENCHMARK", "Experiments completed", "09:42:04"],
  ["DECISION", "Solution C selected", "09:42:17"],
  ["CODER", "Implementation prepared", "09:43:02"],
  ["TESTER", "42 tests passed", "09:43:41"],
];

export default function AIEmployeePreview() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [eventIndex, setEventIndex] = useState(0);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.2 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;

    const interval = window.setInterval(() => {
      setEventIndex((current) =>
        current === EVENTS.length - 1
          ? 0
          : current + 1
      );
    }, 1600);

    return () => clearInterval(interval);
  }, [visible]);

  return (
    <section
      ref={ref}
      className="border-t border-[#161616] bg-[#050505] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="grid items-center gap-16 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                AI EMPLOYEE
              </span>
            </div>

            <h2 className="text-[clamp(3rem,5vw,5.8rem)] font-semibold uppercase leading-[0.88] tracking-[-0.07em] text-white">
              NOT A
              <br />
              CHATBOT.
              <br />
              <span className="text-[#777772]">
                A SYSTEM.
              </span>
            </h2>

            <p className="mt-8 max-w-[500px] text-[14px] leading-7 text-[#696964]">
              KARYA agents can plan, inspect, research, evaluate,
              implement, test and debug inside a controlled
              engineering workflow.
            </p>

            <div className="mt-10 flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />

              <span className="font-mono text-[7px] tracking-[0.2em] text-[#777772]">
                AGENT RUNTIME ACTIVE
              </span>
            </div>
          </div>

          {/* TERMINAL */}

          <div
            className={`
              overflow-hidden
              border
              border-[#282828]
              bg-[#070707]
              shadow-[0_40px_100px_rgba(0,0,0,0.45)]
              transition-all
              duration-[1200ms]
              ${
                visible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-10 opacity-0"
              }
            `}
          >
            <div className="flex h-11 items-center justify-between border-b border-[#222222] px-5">
              <div className="flex gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#393935]" />
                <span className="h-2 w-2 rounded-full bg-[#393935]" />
                <span className="h-2 w-2 rounded-full bg-[#393935]" />
              </div>

              <span className="font-mono text-[7px] tracking-[0.2em] text-[#50504B]">
                KARYA / AGENT TRACE
              </span>

              <span className="font-mono text-[7px] text-[#555550]">
                LIVE
              </span>
            </div>

            <div className="grid min-h-[440px] md:grid-cols-[1fr_0.42fr]">
              <div className="border-r border-[#222222] p-6">
                <div className="mb-8">
                  <span className="font-mono text-[7px] tracking-[0.2em] text-[#464641]">
                    TASK
                  </span>

                  <p className="mt-3 max-w-[470px] font-mono text-[11px] leading-6 text-[#B4B4AF]">
                    Improve API performance while preserving
                    current database behavior and test coverage.
                  </p>
                </div>

                <div className="space-y-5">
                  {EVENTS.map((event, index) => {
                    const active =
                      index === eventIndex;

                    return (
                      <div
                        key={event[0]}
                        className={`
                          flex
                          items-start
                          gap-4
                          transition-all
                          duration-500
                          ${
                            active
                              ? "translate-x-1"
                              : ""
                          }
                        `}
                      >
                        <span
                          className={`
                            mt-1
                            h-1.5
                            w-1.5
                            shrink-0
                            rounded-full
                            transition-all
                            ${
                              active
                                ? "scale-150 bg-white"
                                : "bg-[#454540]"
                            }
                          `}
                        />

                        <div className="min-w-0 flex-1">
                          <div className="flex justify-between gap-4">
                            <span
                              className={`
                                font-mono
                                text-[7px]
                                tracking-[0.16em]
                                ${
                                  active
                                    ? "text-white"
                                    : "text-[#575752]"
                                }
                              `}
                            >
                              {event[0]}
                            </span>

                            <span className="font-mono text-[6px] text-[#393935]">
                              {event[2]}
                            </span>
                          </div>

                          <p className="mt-1 font-mono text-[8px] text-[#666661]">
                            {event[1]}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="p-6">
                <span className="font-mono text-[7px] tracking-[0.2em] text-[#464641]">
                  RUNTIME
                </span>

                <div className="mt-8 space-y-6">
                  {[
                    ["STATE", "EXECUTING"],
                    ["MODEL", "LOCAL"],
                    ["TOOLS", "12"],
                    ["CONTEXT", "94%"],
                    ["TESTS", "42"],
                  ].map(([key, value]) => (
                    <div key={key}>
                      <p className="font-mono text-[6px] tracking-[0.18em] text-[#41413D]">
                        {key}
                      </p>

                      <p className="mt-1 font-mono text-[9px] text-[#D0D0CB]">
                        {value}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-10 border-t border-[#242424] pt-5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[6px] tracking-[0.18em] text-[#464641]">
                      PROGRESS
                    </span>

                    <span className="font-mono text-[8px] text-white">
                      87%
                    </span>
                  </div>

                  <div className="mt-3 h-px bg-[#252525]">
                    <div className="h-full w-[87%] bg-white transition-all duration-1000" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}