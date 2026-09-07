import React, { useEffect, useRef, useState } from "react";

export default function CTA() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.25 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      className="relative overflow-hidden bg-[#050505] py-40 sm:py-52"
    >
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#111111]" />

      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[320px] w-[320px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#171717]" />

      <div className="relative z-10 mx-auto max-w-[1100px] px-6 text-center sm:px-10">
        <div
          className={`
            transition-all
            duration-[1200ms]
            ${
              visible
                ? "translate-y-0 opacity-100"
                : "translate-y-8 opacity-0"
            }
          `}
        >
          <div className="mb-7 flex items-center justify-center gap-3">
            <span className="h-1.5 w-1.5 bg-white" />

            <span className="font-mono text-[8px] tracking-[0.28em] text-[#666661]">
              ENTER THE WORKBENCH
            </span>

            <span className="h-1.5 w-1.5 bg-white" />
          </div>

          <h2 className="text-[clamp(3.5rem,8vw,8rem)] font-semibold uppercase leading-[0.82] tracking-[-0.075em] text-white">
            BUILD WITH
            <br />
            <span className="text-[#777772]">
              INTELLIGENCE.
            </span>
          </h2>

          <p className="mx-auto mt-8 max-w-[560px] text-[14px] leading-7 text-[#666661]">
            Move from asking AI for answers to giving AI
            the context, tools and boundaries required to
            make better decisions.
          </p>

          <a
            href="/app"
            className="
              group
              mx-auto
              mt-10
              inline-flex
              h-14
              items-center
              gap-5
              bg-white
              px-8
              font-mono
              text-[9px]
              font-semibold
              tracking-[0.22em]
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
        </div>
      </div>
    </section>
  );
}