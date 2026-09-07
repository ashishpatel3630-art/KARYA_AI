import React, { useEffect, useRef, useState } from "react";

const ITEMS = [
  "LOCAL-FIRST",
  "PRIVATE BY DESIGN",
  "SOURCE-GROUNDED",
  "AUDITABLE",
  "CONTROLLED EXECUTION",
];

export default function TrustBar() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setVisible(entry.isIntersecting);
      },
      { threshold: 0.35 }
    );

    if (ref.current) observer.observe(ref.current);

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      className="
        relative
        border-y
        border-[#1B1B1B]
        bg-[#080808]
        py-5
      "
    >
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-14">
        <div
          className={`
            flex
            flex-wrap
            items-center
            justify-center
            gap-x-5
            gap-y-3
            transition-all
            duration-1000
            ${
              visible
                ? "translate-y-0 opacity-100"
                : "translate-y-3 opacity-0"
            }
          `}
        >
          {ITEMS.map((item, index) => (
            <React.Fragment key={item}>
              <span className="font-mono text-[7px] tracking-[0.2em] text-[#686863]">
                {item}
              </span>

              {index < ITEMS.length - 1 && (
                <span className="text-[#30302C]">
                  /
                </span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}