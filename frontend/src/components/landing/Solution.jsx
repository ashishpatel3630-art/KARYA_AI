import { ArrowUpRight } from "lucide-react";

function Solution() {
  return (
    <section id="solution" className="border-b border-[#1A1A1A] bg-[#0A0A0A] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        
        <div className="grid gap-16 lg:grid-cols-2 lg:items-end">
          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
              The Solution
            </p>

            <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-6xl">
              An AI employee that actually works.
            </h2>
          </div>

          <p className="max-w-xl text-base leading-7 text-[#8A8A85]">
            KARYA connects your operational systems, understands your
            environment, monitors activity, identifies problems, and executes
            predefined workflows autonomously.
          </p>
        </div>

        <div className="mt-20 grid gap-px bg-[#2A2A2A] md:grid-cols-2 lg:grid-cols-4">
          {[
            ["01", "Observe"],
            ["02", "Understand"],
            ["03", "Decide"],
            ["04", "Execute"],
          ].map(([number, title]) => (
            <div key={number} className="group bg-[#0A0A0A] p-8">
              <span className="text-xs text-[#555]">{number}</span>

              <h3 className="mt-20 flex items-center justify-between text-lg text-white">
                {title}
                <ArrowUpRight
                  size={17}
                  className="text-[#555] transition group-hover:text-white"
                />
              </h3>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Solution;