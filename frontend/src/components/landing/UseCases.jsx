const useCases = [
  {
    number: "01",
    title: "Production",
    text: "Monitor production activity, identify anomalies, and coordinate corrective workflows.",
  },
  {
    number: "02",
    title: "Inventory",
    text: "Track inventory movement, identify shortages, and support procurement decisions.",
  },
  {
    number: "03",
    title: "Quality",
    text: "Analyze quality signals and surface potential issues before they become costly.",
  },
  {
    number: "04",
    title: "Operations",
    text: "Automate repetitive operational tasks and coordinate information across teams.",
  },
];

function UseCases() {
  return (
    <section id="use-cases" className="border-b border-[#1A1A1A] bg-[#050505] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
          Use Cases
        </p>

        <h2 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-6xl">
          One intelligence layer. Multiple operations.
        </h2>

        <div className="mt-20 grid border-l border-t border-[#2A2A2A] md:grid-cols-2">
          {useCases.map((item) => (
            <div
              key={item.number}
              className="border-b border-r border-[#2A2A2A] p-8"
            >
              <span className="text-xs text-[#555]">{item.number}</span>

              <h3 className="mt-20 text-2xl font-medium text-white">
                {item.title}
              </h3>

              <p className="mt-4 max-w-md text-sm leading-6 text-[#8A8A85]">
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default UseCases;