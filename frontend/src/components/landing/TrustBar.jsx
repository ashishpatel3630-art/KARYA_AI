function TrustBar() {
  return (
    <section className="border-b border-[#1A1A1A] bg-[#0A0A0A]">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <p className="text-[10px] uppercase tracking-[0.2em] text-[#555]">
          Built for critical operations
        </p>

        <div className="flex flex-wrap gap-x-10 gap-y-4">
          {["Manufacturing", "Energy", "Logistics", "Infrastructure", "Industrial Operations"].map(
            (item) => (
              <span
                key={item}
                className="text-xs font-medium uppercase tracking-widest text-[#8A8A85]"
              >
                {item}
              </span>
            )
          )}
        </div>
      </div>
    </section>
  );
}

export default TrustBar;