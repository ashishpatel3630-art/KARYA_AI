import React, { useState } from "react";

const USE_CASES = [
  {
    number: "01",
    title: "SOFTWARE ENGINEERING",
    description:
      "Understand repositories, research architecture changes, benchmark solutions and implement controlled improvements.",
  },
  {
    number: "02",
    title: "INDUSTRIAL OPERATIONS",
    description:
      "Bring confidential operational knowledge into a source-grounded AI workflow without losing control.",
  },
  {
    number: "03",
    title: "TECHNICAL RESEARCH",
    description:
      "Transform fragmented documentation and engineering knowledge into actionable decisions.",
  },
  {
    number: "04",
    title: "ENTERPRISE AUTOMATION",
    description:
      "Connect agents to internal tools and workflows through explicit permissions and auditable execution.",
  },
];

export default function UseCases() {
  const [active, setActive] = useState(0);

  return (
    <section className="border-t border-[#161616] bg-[#080808] py-32 sm:py-40">
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="mb-16">
          <div className="mb-7 flex items-center gap-3">
            <span className="h-1.5 w-1.5 bg-white" />

            <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
              USE CASES
            </span>
          </div>

          <h2 className="max-w-[900px] text-[clamp(3rem,5vw,6rem)] font-semibold uppercase leading-[0.88] tracking-[-0.07em] text-white">
            INTELLIGENCE
            <br />
            FOR WORK THAT
            <br />
            <span className="text-[#777772]">
              MATTERS.
            </span>
          </h2>
        </div>

        <div className="grid border border-[#252525] lg:grid-cols-[0.75fr_1.25fr]">
          <div className="border-b border-[#252525] lg:border-b-0 lg:border-r">
            {USE_CASES.map((item, index) => {
              const isActive = active === index;

              return (
                <button
                  key={item.number}
                  type="button"
                  onMouseEnter={() => setActive(index)}
                  className={`
                    flex
                    w-full
                    items-center
                    gap-5
                    border-b
                    border-[#202020]
                    px-6
                    py-6
                    text-left
                    transition-all
                    duration-500
                    last:border-b-0
                    ${
                      isActive
                        ? "bg-[#101010]"
                        : "bg-[#080808]"
                    }
                  `}
                >
                  <span className="font-mono text-[8px] text-[#41413D]">
                    {item.number}
                  </span>

                  <span
                    className={`
                      font-mono
                      text-[9px]
                      font-semibold
                      tracking-[0.17em]
                      ${
                        isActive
                          ? "text-white"
                          : "text-[#62625D]"
                      }
                    `}
                  >
                    {item.title}
                  </span>

                  <span className="ml-auto text-[#444440]">
                    →
                  </span>
                </button>
              );
            })}
          </div>

          <div className="relative min-h-[420px] p-8 sm:p-12">
            <span className="font-mono text-[7px] tracking-[0.2em] text-[#464641]">
              APPLICATION / 0{active + 1}
            </span>

            <h3 className="mt-20 max-w-[600px] text-[clamp(2rem,3.8vw,4rem)] font-semibold uppercase leading-[0.92] tracking-[-0.06em] text-white">
              {USE_CASES[active].title}
            </h3>

            <p className="mt-6 max-w-[560px] text-[13px] leading-7 text-[#686863]">
              {USE_CASES[active].description}
            </p>

            <div className="absolute bottom-8 left-8 right-8 border-t border-[#222222] pt-4 sm:left-12 sm:right-12">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[6px] tracking-[0.18em] text-[#454540]">
                  KARYA CORE
                </span>

                <span className="font-mono text-[6px] tracking-[0.18em] text-[#454540]">
                  ACTIVE
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}