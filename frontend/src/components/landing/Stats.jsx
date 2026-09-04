function Stats() {
  const stats = [
    ["99.8%", "System Health"],
    ["1,842+", "Tasks Processed"],
    ["24/7", "Operational Monitoring"],
    ["04", "AI Employees"],
  ];

  return (
    <section className="border-b border-[#1A1A1A] bg-[#0A0A0A]">
      <div className="mx-auto grid max-w-7xl grid-cols-2 border-l border-[#2A2A2A] lg:grid-cols-4">
        {stats.map(([value, label]) => (
          <div
            key={label}
            className="border-r border-[#2A2A2A] px-6 py-12"
          >
            <p className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              {value}
            </p>

            <p className="mt-3 text-[10px] uppercase tracking-[0.2em] text-[#555]">
              {label}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Stats;