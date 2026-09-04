function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Connect",
      text: "Connect KARYA to your existing operational systems and data sources.",
    },
    {
      number: "02",
      title: "Configure",
      text: "Define business rules, workflows, permissions, and operational objectives.",
    },
    {
      number: "03",
      title: "Deploy",
      text: "Deploy specialized AI employees for specific operational functions.",
    },
    {
      number: "04",
      title: "Operate",
      text: "KARYA continuously monitors, reasons, and executes tasks.",
    },
  ];

  return (
    <section className="border-b border-[#1A1A1A] bg-[#0A0A0A] py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <p className="text-[10px] uppercase tracking-[0.25em] text-[#f43131]">
          How It Works
        </p>

        <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-6xl">
          From data to action.
        </h2>

        <div className="mt-20">
          {steps.map((step) => (
            <div
              key={step.number}
              className="grid border-t border-[#2A2A2A] py-8 md:grid-cols-[100px_250px_1fr]"
            >
              <span className="text-xs text-[#555]">{step.number}</span>

              <h3 className="mt-4 text-xl font-medium text-white md:mt-0">
                {step.title}
              </h3>

              <p className="mt-4 max-w-xl text-sm leading-6 text-[#8A8A85] md:mt-0">
                {step.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;