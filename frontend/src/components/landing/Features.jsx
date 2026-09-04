import {
  Activity,
  Brain,
  Database,
  Workflow,
  Shield,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: Activity,
    title: "Continuous Monitoring",
    description:
      "Monitor operational systems and detect important changes in real time.",
  },
  {
    icon: Brain,
    title: "Operational Intelligence",
    description:
      "Transform raw operational data into contextual decisions and recommendations.",
  },
  {
    icon: Database,
    title: "Data Intelligence",
    description:
      "Connect databases, APIs, documents, sensors, and internal systems.",
  },
  {
    icon: Workflow,
    title: "Autonomous Workflows",
    description:
      "Trigger and execute predefined operational workflows automatically.",
  },
  {
    icon: Shield,
    title: "Confidential by Design",
    description:
      "Keep sensitive operational intelligence protected with controlled access.",
  },
  {
    icon: BarChart3,
    title: "Performance Intelligence",
    description:
      "Track operational performance, anomalies, trends, and system health.",
  },
];

function Features() {
  return (
    <section id="features" className="border-b border-[#1A1A1A] bg-[#050505] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
            Capabilities
          </p>

          <h2 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-6xl">
            Intelligence built around the operation.
          </h2>
        </div>

        <div className="mt-20 grid border-l border-t border-[#2A2A2A] md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className="border-b border-r border-[#2A2A2A] p-8"
              >
                <Icon size={22} className="text-[#8A8A85]" />

                <h3 className="mt-14 text-lg font-medium text-white">
                  {feature.title}
                </h3>

                <p className="mt-4 text-sm leading-6 text-[#8A8A85]">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default Features;