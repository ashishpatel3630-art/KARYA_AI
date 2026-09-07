import React, { useEffect, useRef, useState } from "react";

const PROBLEMS = [
  {
    number: "01",
    title: "FRAGMENTED KNOWLEDGE",
    text: "Critical information lives across repositories, documents, systems and teams.",
  },
  {
    number: "02",
    title: "SLOW ENGINEERING DECISIONS",
    text: "Teams spend valuable time understanding context before they can act.",
  },
  {
    number: "03",
    title: "UNCONTROLLED AI EXECUTION",
    text: "Generic AI tools lack the security, traceability and execution boundaries industrial work requires.",
  },
];

export default function Problem() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.18 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      className="relative overflow-hidden bg-[#050505] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="grid gap-16 lg:grid-cols-[0.8fr_1.2fr]">
          <div
            className={`
              transition-all
              duration-1000
              ${
                visible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-8 opacity-0"
              }
            `}
          >
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                THE PROBLEM
              </span>
            </div>

            <h2 className="max-w-[620px] text-[clamp(2.8rem,5vw,5.8rem)] font-semibold uppercase leading-[0.9] tracking-[-0.065em] text-white">
              INDUSTRIAL WORK
              <br />
              <span className="text-[#74746F]">
                CANNOT RUN ON
              </span>
              <br />
              GENERIC AI.
            </h2>
          </div>

          <div className="border-l border-[#202020] pl-6 sm:pl-10">
            <p
              className={`
                max-w-[580px]
                text-[15px]
                leading-7
                text-[#858580]
                transition-all
                delay-200
                duration-1000
                ${
                  visible
                    ? "translate-y-0 opacity-100"
                    : "translate-y-8 opacity-0"
                }
              `}
            >
              Confidential engineering environments need more
              than generated answers. They need intelligence that
              understands context, retrieves evidence, evaluates
              alternatives and executes within controlled boundaries.
            </p>

            <div className="mt-14">
              {PROBLEMS.map((problem, index) => (
                <div
                  key={problem.number}
                  className={`
                    group
                    border-t
                    border-[#202020]
                    py-7
                    transition-all
                    duration-1000
                    ${
                      visible
                        ? "translate-x-0 opacity-100"
                        : "translate-x-8 opacity-0"
                    }
                  `}
                  style={{
                    transitionDelay: `${300 + index * 120}ms`,
                  }}
                >
                  <div className="grid gap-5 sm:grid-cols-[70px_1fr]">
                    <span className="font-mono text-[8px] text-[#454540]">
                      {problem.number}
                    </span>

                    <div>
                      <h3 className="font-mono text-[10px] font-semibold tracking-[0.18em] text-[#D0D0CB] transition-colors duration-300 group-hover:text-white">
                        {problem.title}
                      </h3>

                      <p className="mt-3 max-w-[470px] text-[13px] leading-6 text-[#666661]">
                        {problem.text}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}