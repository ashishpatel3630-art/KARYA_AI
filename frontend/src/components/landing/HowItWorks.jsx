import React, { useEffect, useRef, useState } from "react";

const STEPS = [
  ["01", "CONNECT", "Connect a repository and establish the project context."],
  ["02", "ANALYZE", "Map architecture, dependencies, files and system relationships."],
  ["03", "RESEARCH", "Retrieve relevant knowledge and investigate possible approaches."],
  ["04", "COMPARE", "Generate multiple solutions and evaluate trade-offs."],
  ["05", "BENCHMARK", "Measure performance, cost, complexity and test impact."],
  ["06", "DECIDE", "Select the strongest engineering path."],
  ["07", "EXECUTE", "Implement through controlled tools and sandboxed execution."],
  ["08", "VERIFY", "Test, debug, review and prepare the final change."],
];

export default function HowItWorks() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [active, setActive] = useState(0);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.15 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;

    const interval = window.setInterval(() => {
      setActive((current) =>
        current === STEPS.length - 1
          ? 0
          : current + 1
      );
    }, 1800);

    return () => clearInterval(interval);
  }, [visible]);

  return (
    <section
      id="how-it-works"
      ref={ref}
      className="relative overflow-hidden bg-[#050505] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="grid gap-16 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                HOW IT WORKS
              </span>
            </div>

            <h2
              className={`
                text-[clamp(3rem,5.5vw,6rem)]
                font-semibold
                uppercase
                leading-[0.88]
                tracking-[-0.07em]
                transition-all
                duration-1000
                ${
                  visible
                    ? "translate-y-0 opacity-100"
                    : "translate-y-10 opacity-0"
                }
              `}
            >
              ONE
              <br />
              CONTINUOUS
              <br />
              <span className="text-[#777772]">
                INTELLIGENCE LOOP.
              </span>
            </h2>

            <p className="mt-8 max-w-[500px] text-[14px] leading-7 text-[#666661]">
              KARYA turns an engineering problem into a
              structured decision and execution pipeline.
            </p>
          </div>

          <div className="relative">
            <div className="absolute left-[18px] top-5 bottom-5 w-px bg-[#222222]" />

            {STEPS.map((step, index) => {
              const isActive = active === index;

              return (
                <button
                  key={step[0]}
                  type="button"
                  onMouseEnter={() => setActive(index)}
                  className={`
                    group
                    relative
                    flex
                    w-full
                    items-start
                    gap-7
                    py-4
                    text-left
                    transition-all
                    duration-500
                    ${
                      visible
                        ? "translate-x-0 opacity-100"
                        : "translate-x-8 opacity-0"
                    }
                  `}
                  style={{
                    transitionDelay: `${index * 80}ms`,
                  }}
                >
                  <span
                    className={`
                      relative
                      z-10
                      mt-1
                      flex
                      h-9
                      w-9
                      shrink-0
                      items-center
                      justify-center
                      rounded-full
                      border
                      bg-[#050505]
                      font-mono
                      text-[7px]
                      transition-all
                      duration-500
                      ${
                        isActive
                          ? "border-white text-white"
                          : "border-[#333333] text-[#555550]"
                      }
                    `}
                  >
                    {step[0]}
                  </span>

                  <div className="flex-1 border-b border-[#191919] pb-5">
                    <div className="flex items-center justify-between gap-4">
                      <h3
                        className={`
                          font-mono
                          text-[10px]
                          font-semibold
                          tracking-[0.2em]
                          transition-colors
                          ${
                            isActive
                              ? "text-white"
                              : "text-[#696964]"
                          }
                        `}
                      >
                        {step[1]}
                      </h3>

                      <span
                        className={`
                          font-mono
                          text-[7px]
                          transition-all
                          ${
                            isActive
                              ? "translate-x-0 opacity-100"
                              : "-translate-x-2 opacity-0"
                          }
                        `}
                      >
                        ACTIVE
                      </span>
                    </div>

                    <p
                      className={`
                        mt-2
                        max-w-[540px]
                        text-[12px]
                        leading-6
                        transition-colors
                        ${
                          isActive
                            ? "text-[#858580]"
                            : "text-[#4D4D49]"
                        }
                      `}
                    >
                      {step[2]}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}