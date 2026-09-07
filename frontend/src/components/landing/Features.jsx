import React, { useEffect, useRef, useState } from "react";

const FEATURES = [
  {
    id: "01",
    title: "REPOSITORY INTELLIGENCE",
    description:
      "Understand the structure of real systems before acting on them.",
    tags: ["AST", "DEPENDENCIES", "ARCHITECTURE"],
  },
  {
    id: "02",
    title: "CODE RAG",
    description:
      "Retrieve relevant code and documentation context instead of loading entire repositories.",
    tags: ["EMBEDDINGS", "PGVECTOR", "SEMANTIC SEARCH"],
  },
  {
    id: "03",
    title: "MULTI-SOLUTION RESEARCH",
    description:
      "Generate competing engineering approaches and compare their trade-offs.",
    tags: ["RESEARCH", "DECISION", "TRADE-OFFS"],
  },
  {
    id: "04",
    title: "BENCHMARK ENGINE",
    description:
      "Measure latency, throughput, memory, cost, complexity and test impact.",
    tags: ["LATENCY", "CPU", "MEMORY"],
  },
  {
    id: "05",
    title: "CONTROLLED EXECUTION",
    description:
      "Run AI-generated changes through permission checks and isolated environments.",
    tags: ["SANDBOX", "POLICY", "PERMISSIONS"],
  },
  {
    id: "06",
    title: "AGENT TRACE",
    description:
      "Maintain a complete decision trail from planning through implementation.",
    tags: ["TRACE", "AUDIT", "OBSERVABILITY"],
  },
];

export default function Features() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.15 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="capabilities"
      ref={ref}
      className="border-t border-[#161616] bg-[#080808] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="mb-16 flex flex-col justify-between gap-8 lg:flex-row lg:items-end">
          <div>
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                CORE CAPABILITIES
              </span>
            </div>

            <h2 className="max-w-[800px] text-[clamp(3rem,5vw,5.7rem)] font-semibold uppercase leading-[0.88] tracking-[-0.07em] text-white">
              BUILT FOR
              <br />
              <span className="text-[#777772]">
                REAL ENGINEERING.
              </span>
            </h2>
          </div>

          <span className="font-mono text-[8px] tracking-[0.2em] text-[#41413D]">
            06 SYSTEMS
          </span>
        </div>

        <div className="grid gap-px bg-[#242424] md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, index) => (
            <article
              key={feature.id}
              className={`
                group
                relative
                min-h-[300px]
                bg-[#080808]
                p-7
                transition-all
                duration-1000
                hover:bg-[#0C0C0C]
                ${
                  visible
                    ? "translate-y-0 opacity-100"
                    : "translate-y-8 opacity-0"
                }
              `}
              style={{
                transitionDelay: `${index * 100}ms`,
              }}
            >
              <div className="flex items-start justify-between">
                <span className="font-mono text-[8px] text-[#454540]">
                  {feature.id}
                </span>

                <span className="font-mono text-[7px] text-[#383834]">
                  KRY
                </span>
              </div>

              <div className="mt-20">
                <h3 className="max-w-[260px] font-mono text-[11px] font-semibold tracking-[0.16em] text-[#D0D0CB] transition-colors duration-500 group-hover:text-white">
                  {feature.title}
                </h3>

                <p className="mt-4 max-w-[310px] text-[12px] leading-6 text-[#60605B]">
                  {feature.description}
                </p>
              </div>

              <div className="absolute bottom-7 left-7 flex flex-wrap gap-2">
                {feature.tags.map((tag) => (
                  <span
                    key={tag}
                    className="border border-[#292929] px-2 py-1 font-mono text-[6px] tracking-[0.15em] text-[#50504B]"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <span className="absolute right-7 top-20 h-px w-0 bg-[#777772] transition-all duration-700 group-hover:w-12" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}