import { Bot, CheckCircle2 } from "lucide-react";

const agents = [
  "Production Monitor",
  "Inventory Intelligence",
  "Quality Analysis",
  "Operations Assistant",
];

function AIEmployeePreview() {
  return (
    <section className="border-b border-[#1A1A1A] bg-[#050505] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        
        <div className="grid gap-16 lg:grid-cols-2 lg:items-center">
          
          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
              AI Workforce
            </p>

            <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-6xl">
              Deploy AI employees for every operation.
            </h2>

            <p className="mt-6 max-w-xl text-sm leading-7 text-[#8A8A85]">
              Instead of one general-purpose assistant, KARYA creates
              specialized AI employees designed around individual operational
              responsibilities.
            </p>
          </div>

          <div className="border border-[#2A2A2A] bg-[#0A0A0A]">
            <div className="flex items-center gap-3 border-b border-[#2A2A2A] p-5">
              <Bot size={18} className="text-[#8A8A85]" />
              <div>
                <p className="text-xs font-medium text-white">
                  AI Workforce
                </p>
                <p className="text-[9px] uppercase tracking-widest text-[#555]">
                  4 agents active
                </p>
              </div>
            </div>

            <div className="divide-y divide-[#1A1A1A]">
              {agents.map((agent) => (
                <div
                  key={agent}
                  className="flex items-center justify-between p-5"
                >
                  <span className="text-sm text-[#F5F5F5]">{agent}</span>

                  <CheckCircle2 size={15} className="text-[#8A8A85]" />
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}

export default AIEmployeePreview;