import { Lock, Server, UserCheck } from "lucide-react";

function Security() {
  return (
    <section id="security" className="border-b border-[#1A1A1A] bg-[#0A0A0A] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        
        <div className="max-w-3xl">
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
            Security
          </p>

          <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-6xl">
            Your operational intelligence stays yours.
          </h2>

          <p className="mt-6 text-base leading-7 text-[#8A8A85]">
            KARYA is designed around confidentiality, controlled access,
            isolated workloads, and operational governance.
          </p>
        </div>

        <div className="mt-20 grid gap-px bg-[#2A2A2A] md:grid-cols-3">
          {[
            {
              icon: Lock,
              title: "Controlled Access",
              text: "Define exactly what each AI employee can access and execute.",
            },
            {
              icon: Server,
              title: "Isolated Systems",
              text: "Keep sensitive workloads separated from unrelated operations.",
            },
            {
              icon: UserCheck,
              title: "Human Oversight",
              text: "Critical actions can remain subject to human approval.",
            },
          ].map((item) => {
            const Icon = item.icon;

            return (
              <div key={item.title} className="bg-[#0A0A0A] p-8">
                <Icon size={22} className="text-[#8A8A85]" />

                <h3 className="mt-14 text-lg text-white">
                  {item.title}
                </h3>

                <p className="mt-4 text-sm leading-6 text-[#8A8A85]">
                  {item.text}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default Security;