import React from "react";

const COLUMNS = [
  {
    title: "PLATFORM",
    links: [
      "Product",
      "Capabilities",
      "How It Works",
      "Use Cases",
    ],
  },
  {
    title: "SYSTEM",
    links: [
      "Security",
      "Architecture",
      "Agent Runtime",
      "Documentation",
    ],
  },
  {
    title: "COMPANY",
    links: [
      "About",
      "Contact",
      "Careers",
      "Status",
    ],
  },
];

export default function Footer({ onLogin }) {
  const scrollTo = (label) => {
    const map = {
      Product: "product",
      Capabilities: "capabilities",
      "How It Works": "how-it-works",
      Security: "security",
      "Use Cases": "use-cases",
    };

    const target = map[label];

    if (!target) return;

    document
      .getElementById(target)
      ?.scrollIntoView({
        behavior: "smooth",
      });
  };

  return (
    <footer className="border-t border-[#202020] bg-[#050505]">
      <div className="mx-auto max-w-[1500px] px-6 py-20 sm:px-10 lg:px-14">
        <div className="grid gap-16 lg:grid-cols-[1.2fr_1fr]">
          <div>
            <button
              type="button"
              onClick={() =>
                window.scrollTo({
                  top: 0,
                  behavior: "smooth",
                })
              }
              className="flex items-center gap-3"
            >
              <span className="flex h-10 w-10 items-center justify-center border border-[#3A3A3A] font-semibold text-white">
                K
              </span>

              <span className="font-mono text-[11px] font-semibold tracking-[0.3em] text-white">
                KARYA
              </span>
            </button>

            <p className="mt-7 max-w-[470px] text-[13px] leading-7 text-[#5F5F5A]">
              The sovereign AI workforce for industrial work.
              Local intelligence, agentic execution and
              source-grounded results for confidential
              environments.
            </p>

            <div className="mt-8 flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />

              <span className="font-mono text-[7px] tracking-[0.2em] text-[#5B5B56]">
                SYSTEM OPERATIONAL
              </span>
            </div>

            <button
              type="button"
              onClick={() => {
                if (onLogin) {
                  onLogin();
                  return;
                }

                window.location.href = "/login";
              }}
              className="mt-8 border border-[#383838] px-4 py-3 font-mono text-[8px] font-semibold uppercase tracking-[0.18em] text-white transition hover:border-white hover:bg-white hover:text-black"
            >
              LOGIN TO KARYA →
            </button>
          </div>

          <div className="grid grid-cols-2 gap-10 sm:grid-cols-3">
            {COLUMNS.map((column) => (
              <div key={column.title}>
                <h3 className="font-mono text-[7px] font-semibold tracking-[0.2em] text-[#777772]">
                  {column.title}
                </h3>

                <div className="mt-6 space-y-4">
                  {column.links.map((link) => (
                    <button
                      key={link}
                      type="button"
                      onClick={() => scrollTo(link)}
                      className="block font-mono text-[8px] tracking-[0.12em] text-[#4F4F4A] transition-colors duration-300 hover:text-white"
                    >
                      {link}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-20 border-t border-[#1D1D1D] pt-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row">
            <span className="font-mono text-[7px] tracking-[0.2em] text-[#41413D]">
              © 2026 KARYA AI
            </span>

            <div className="flex flex-wrap gap-5">
              <span className="font-mono text-[7px] tracking-[0.18em] text-[#41413D]">
                LOCAL
              </span>

              <span className="font-mono text-[7px] text-[#292925]">
                /
              </span>

              <span className="font-mono text-[7px] tracking-[0.18em] text-[#41413D]">
                PRIVATE
              </span>

              <span className="font-mono text-[7px] text-[#292925]">
                /
              </span>

              <span className="font-mono text-[7px] tracking-[0.18em] text-[#41413D]">
                INDUSTRIAL
              </span>

              <span className="font-mono text-[7px] text-[#292925]">
                /
              </span>

              <span className="font-mono text-[7px] tracking-[0.18em] text-[#41413D]">
                AUDITABLE
              </span>
            </div>

            <span className="font-mono text-[7px] tracking-[0.2em] text-[#41413D]">
              KRY // SYS
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}