import React, { useEffect, useRef, useState } from "react";

const SECURITY = [
  ["01", "LOCAL EXECUTION", "Keep sensitive workloads within controlled environments."],
  ["02", "ZERO-TRUST TOOLS", "Every external capability is exposed through explicit boundaries."],
  ["03", "SANDBOXED CODE", "AI-generated execution is isolated from the host environment."],
  ["04", "HUMAN APPROVAL", "Sensitive changes remain subject to explicit human authorization."],
  ["05", "AUDIT TRAIL", "Decisions, tool calls and execution events remain traceable."],
];

export default function Security() {
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
      id="security"
      ref={ref}
      className="relative overflow-hidden border-t border-[#161616] bg-[#050505] py-32 sm:py-40"
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div className="grid gap-16 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <div className="mb-7 flex items-center gap-3">
              <span className="h-1.5 w-1.5 bg-white" />

              <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
                SECURITY
              </span>
            </div>

            <h2 className="text-[clamp(3rem,5vw,6rem)] font-semibold uppercase leading-[0.87] tracking-[-0.07em] text-white">
              INTELLIGENCE
              <br />
              WITHOUT
              <br />
              <span className="text-[#777772]">
                LOSING CONTROL.
              </span>
            </h2>

            <p className="mt-8 max-w-[500px] text-[14px] leading-7 text-[#666661]">
              Security is not a layer added after the AI.
              It is part of how KARYA executes.
            </p>
          </div>

          <div>
            {SECURITY.map((item, index) => (
              <div
                key={item[0]}
                className={`
                  group
                  border-t
                  border-[#242424]
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
                  transitionDelay: `${index * 100}ms`,
                }}
              >
                <div className="grid gap-5 sm:grid-cols-[60px_0.8fr_1.2fr]">
                  <span className="font-mono text-[7px] text-[#41413D]">
                    {item[0]}
                  </span>

                  <h3 className="font-mono text-[9px] font-semibold tracking-[0.17em] text-[#BDBDB8] group-hover:text-white">
                    {item[1]}
                  </h3>

                  <p className="text-[12px] leading-6 text-[#5F5F5A]">
                    {item[2]}
                  </p>
                </div>
              </div>
            ))}

            <div className="border-t border-[#242424] pt-6">
              <div className="flex items-center gap-3">
                <span className="h-1.5 w-1.5 bg-white" />

                <span className="font-mono text-[7px] tracking-[0.2em] text-[#777772]">
                  SECURITY ARCHITECTURE ACTIVE
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}