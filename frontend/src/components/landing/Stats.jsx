import React, { useEffect, useRef, useState } from "react";

const STATS = [
  {
    value: "18",
    label: "CORE SYSTEMS",
  },
  {
    value: "11",
    label: "AGENT ROLES",
  },
  {
    value: "∞",
    label: "ENGINEERING CONTEXT",
  },
  {
    value: "01",
    label: "DECISION ENGINE",
  },
];

function Counter({ value, active }) {
  const [display, setDisplay] = useState(
    value === "∞" ? "∞" : "00"
  );

  useEffect(() => {
    if (!active || value === "∞") {
      setDisplay(value === "∞" ? "∞" : "00");
      return;
    }

    const target = Number(value);
    const start = performance.now();
    const duration = 1100;

    const animate = (now) => {
      const progress = Math.min(
        (now - start) / duration,
        1
      );

      const eased =
        1 - Math.pow(1 - progress, 3);

      const current = Math.floor(target * eased);

      setDisplay(
        String(current).padStart(2, "0")
      );

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [active, value]);

  return <>{display}</>;
}

export default function Stats() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.35 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      className="border-y border-[#1B1B1B] bg-[#080808]"
    >
      <div className="mx-auto grid max-w-[1500px] grid-cols-2 gap-px bg-[#242424] lg:grid-cols-4">
        {STATS.map((stat, index) => (
          <div
            key={stat.label}
            className={`
              bg-[#080808]
              px-6
              py-12
              transition-all
              duration-1000
              sm:px-10
              lg:py-16
              ${
                visible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-5 opacity-0"
              }
            `}
            style={{
              transitionDelay: `${index * 120}ms`,
            }}
          >
            <div className="font-sans text-[clamp(3rem,5vw,5rem)] font-semibold tracking-[-0.07em] text-white">
              <Counter
                value={stat.value}
                active={visible}
              />
            </div>

            <div className="mt-4 font-mono text-[7px] tracking-[0.2em] text-[#555550]">
              {stat.label}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}