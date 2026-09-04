function Problem() {
  const problems = [
    {
      number: "01",
      title: "Fragmented Operations",
      description:
        "Critical information is distributed across dashboards, databases, machines, documents, and teams.",
    },
    {
      number: "02",
      title: "Slow Decisions",
      description:
        "Human teams spend valuable time collecting information before they can act on it.",
    },
    {
      number: "03",
      title: "Reactive Workflows",
      description:
        "Most operational systems report what happened instead of continuously identifying what should happen next.",
    },
  ];

  return (
    <section className="border-b border-[#1A1A1A] bg-[#050505] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="max-w-2xl">
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
            The Problem
          </p>

          <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Industrial operations are drowning in information.
          </h2>
        </div>

        <div className="mt-20 grid border-l border-t border-[#2A2A2A] md:grid-cols-3">
          {problems.map((problem) => (
            <div
              key={problem.number}
              className="border-b border-r border-[#2A2A2A] p-8"
            >
              <span className="text-xs text-[#555]">{problem.number}</span>

              <h3 className="mt-16 text-xl font-medium text-white">
                {problem.title}
              </h3>

              <p className="mt-4 text-sm leading-6 text-[#8A8A85]">
                {problem.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Problem;