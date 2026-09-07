import React, { useEffect, useRef, useState } from "react";

const LAYERS = [
  {
    id: "01",
    title: "UNDERSTAND",
    description:
      "Repository intelligence maps files, dependencies, architecture and operational context.",
  },
  {
    id: "02",
    title: "REASON",
    description:
      "Source-grounded retrieval gives agents the context required to make engineering decisions.",
  },
  {
    id: "03",
    title: "DECIDE",
    description:
      "Multiple solutions are generated, compared and evaluated before implementation.",
  },
  {
    id: "04",
    title: "EXECUTE",
    description:
      "Controlled agents implement, test, debug and prepare changes for human approval.",
  },
];

export default function Solution() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [active, setActive] = useState(0);

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
      setActive((current) =>
        current === LAYERS.length - 1
          ? 0
          : current + 1
      );
    }, 2600);

    return () => clearInterval(interval);
  }, [visible]);

  return (
    <section
      id="product"
      ref={ref}
      className="relative overflow-hidden border-t border-[#151515] bg-[#080808] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="mb-20 flex items-end justify-between gap-8">
          <div>
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                THE KARYA APPROACH
              </span>
            </div>

            <h2
              className={`
                max-w-[850px]
                text-[clamp(2.8rem,5.5vw,6.2rem)]
                font-semibold
                uppercase
                leading-[0.88]
                tracking-[-0.07em]
                text-white
                transition-all
                duration-1000
                ${
                  visible
                    ? "translate-y-0 opacity-100"
                    : "translate-y-8 opacity-0"
                }
              `}
            >
              FROM
              <br />
              <span className="text-[#777772]">
                QUESTION
              </span>
              <br />
              TO DECISION.
            </h2>
          </div>

          <span className="hidden font-mono text-[8px] tracking-[0.2em] text-[#444440] lg:block">
            KRY / 002
          </span>
        </div>

        <div className="grid gap-12 lg:grid-cols-[0.75fr_1.25fr]">
          {/* LAYERS */}

          <div>
            {LAYERS.map((layer, index) => {
              const isActive = active === index;

              return (
                <button
                  key={layer.id}
                  type="button"
                  onMouseEnter={() => setActive(index)}
                  className={`
                    group
                    flex
                    w-full
                    items-center
                    gap-5
                    border-t
                    py-6
                    text-left
                    transition-all
                    duration-500
                    ${
                      isActive
                        ? "border-[#777777]"
                        : "border-[#222222]"
                    }
                  `}
                >
                  <span
                    className={`
                      font-mono
                      text-[8px]
                      transition-colors
                      ${
                        isActive
                          ? "text-white"
                          : "text-[#444440]"
                      }
                    `}
                  >
                    {layer.id}
                  </span>

                  <span
                    className={`
                      font-mono
                      text-[10px]
                      font-semibold
                      tracking-[0.18em]
                      transition-colors
                      ${
                        isActive
                          ? "text-white"
                          : "text-[#666661]"
                      }
                    `}
                  >
                    {layer.title}
                  </span>

                  <span
                    className={`
                      ml-auto
                      transition-all
                      duration-500
                      ${
                        isActive
                          ? "translate-x-0 opacity-100"
                          : "-translate-x-2 opacity-0"
                      }
                    `}
                  >
                    →
                  </span>
                </button>
              );
            })}
          </div>

          {/* VISUAL */}

          <div className="relative min-h-[440px] border border-[#252525] bg-[#050505]">
            <div className="absolute left-0 top-0 h-16 w-16 border-l border-t border-[#444440]" />

            <div className="absolute bottom-0 right-0 h-16 w-16 border-b border-r border-[#444440]" />

            <div className="absolute inset-0 flex items-center justify-center">
              <div className="relative h-[270px] w-[270px]">
                <div className="absolute inset-0 animate-[spin_35s_linear_infinite] rounded-full border border-dashed border-[#333333]" />

                <div className="absolute inset-[35px] rounded-full border border-[#292929]" />

                <div className="absolute inset-[75px] rotate-45 border border-[#6A6A65]" />

                <div className="absolute left-1/2 top-1/2 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center border border-[#777772]">
                  <span className="font-sans text-2xl font-semibold">
                    K
                  </span>
                </div>

                {[0, 1, 2, 3].map((index) => {
                  const positions = [
                    "left-1/2 top-0 -translate-x-1/2",
                    "right-0 top-1/2 -translate-y-1/2",
                    "bottom-0 left-1/2 -translate-x-1/2",
                    "left-0 top-1/2 -translate-y-1/2",
                  ];

                  return (
                    <span
                      key={index}
                      className={`
                        absolute
                        h-2
                        w-2
                        rounded-full
                        transition-all
                        duration-700
                        ${
                          active === index
                            ? "scale-150 bg-white"
                            : "bg-[#555550]"
                        }
                        ${positions[index]}
                      `}
                    />
                  );
                })}
              </div>
            </div>

            <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
              <div>
                <p className="font-mono text-[7px] tracking-[0.2em] text-[#4F4F4A]">
                  ACTIVE LAYER
                </p>

                <p className="mt-2 font-mono text-[9px] font-semibold tracking-[0.18em] text-white">
                  {LAYERS[active].title}
                </p>
              </div>

              <span className="font-mono text-[7px] tracking-[0.18em] text-[#454540]">
                0{active + 1} / 04
              </span>
            </div>
          </div>
        </div>

        <p className="mt-10 max-w-[650px] text-[13px] leading-6 text-[#666661]">
          KARYA is designed around engineering decision-making,
          not simply code generation. It understands the system,
          researches alternatives, benchmarks approaches and
          executes the selected path inside controlled boundaries.
        </p>
      </div>
    </section>
  );
}